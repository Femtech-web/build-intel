import os
import httpx # pyright: ignore[reportMissingImports]
import logging
import json

logger = logging.getLogger(__name__)

class LLMProvider:
    """LLM provider using Fireworks.ai to generate project insights."""

    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.fireworks.ai/inference/v1/completions")
        self.model = os.getenv("LLM_MODEL", "accounts/fireworks/models/llama-v3p1-70b-instruct")

    async def generate_insight(self, project_name, github, twitter, funding):
        """Generate a full insight summary (non-streamed) for a project."""
        prompt = f"""
        Generate an honest, analytical summary of the crypto project '{project_name}'
        using this data:
        GitHub: {json.dumps(github, indent=2)}
        Twitter: {json.dumps(twitter, indent=2)}
        Funding: {json.dumps(funding, indent=2)}

        The summary should be written in markdown with sections for:
        - Overview
        - Development
        - Community
        - Funding Insight

        Please write the report **directly starting with the 'Overview' section** (do not include any 'Summary' or introduction text).
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": 700,
            "temperature": 0.7,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            resp = await client.post(self.base_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("choices", [{}])[0].get("text", "No insight generated.")

    async def extract_funding_details(self, project_name: str, raw_sources: dict) -> dict:
        """
        Enhanced funding intelligence extraction.
        - Pre-parses funding-related snippets (esp. from SerpAPI)
        - Detects dollar amounts, funding rounds, and investor names via regex
        - Guides LLM to produce confident, structured JSON output
        """

        import re

        if not raw_sources:
            return {"error": "No funding data available"}

        # Helper: Extract relevant snippets from SerpAPI 
        def _extract_text_snippets(source):
            if not source:
                return []
            results = source.get("results", [])
            return [r.get("snippet", "") for r in results if isinstance(r, dict) and "snippet" in r]

        serpapi_snippets = _extract_text_snippets(raw_sources.get("serpapi"))
        text_snippets = "\n".join(serpapi_snippets[:8])  # cap at 8 for brevity

        # Regex-based funding clue extraction\
        def detect_funding_clues(snippets: str):
            rounds = re.findall(r"(Series\s+[A-Z])", snippets, re.I)
            amounts = re.findall(r"\$[0-9]+(?:\.[0-9]+)?\s*(?:M|million|B|billion)?", snippets, re.I)
            investors = [
                m.group(0) for m in re.finditer(
                    r"\b(Sequoia|Paradigm|a16z|Binance\s+Labs|Coinbase\s+Ventures|Andreessen\s+Horowitz|Polychain|Dragonfly|Pantera)\b",
                    snippets, re.I
                )
            ]
            return {
                "rounds": list(set(rounds)),
                "amounts": list(set(amounts)),
                "investors": list(set(investors)),
            }

        funding_hints = detect_funding_clues(text_snippets)

        # Construct LLM prompt
        prompt = f"""
        You are a financial intelligence agent.
        Given structured funding data from multiple APIs and text snippets for **{project_name}**, infer the most accurate funding summary.

        ## Data sources may include:
        - DeFiLlama (protocol metrics)
        - CoinGecko (token info, description, market data)
        - SerpAPI (funding news and investor details)

        ## Hints (from regex pre-scan)
        {json.dumps(funding_hints, indent=2)}

        ## Textual funding snippets
        {text_snippets}

        ## Full structured data
        {json.dumps(raw_sources, indent=2)}

        Analyze this data carefully and return only valid JSON with this structure:

        {{
            "project": "{project_name}",
            "summary": "Concise human-readable summary of its funding and investors.",
            "details": {{
                "total_funding": "<e.g. '$19M' or 'Unknown'>",
                "last_round": "<e.g. 'Series A' or 'Seed'>",
                "investors": ["<investor1>", "<investor2>", "..."],
                "notable_backers": ["<known top funds>"],
                "funding_sources": ["defillama", "coingecko", "serpapi"]
            }}
        }}
        Be factual and confident if any evidence clearly supports it.
        Return only valid JSON, no commentary or markdown.
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": 900,
            "temperature": 0.3,
            "stream": False
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(self.base_url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                text_output = data.get("choices", [{}])[0].get("text", "")

                # Step 1: Try direct JSON parse
                try:
                    result = json.loads(text_output)
                    if isinstance(result, dict):
                        parsed = result
                    else:
                        raise ValueError
                except Exception:
                    # Step 2: Clean up malformed JSON
                    cleaned = text_output.strip()
                    cleaned = cleaned.split("```")[-1]
                    cleaned = cleaned.replace("```json", "").replace("```", "").strip()
                    cleaned = cleaned.replace("\n", " ").replace("\r", " ")
                    try:
                        parsed = json.loads(cleaned)
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ JSON parse failed for {project_name}")
                        parsed = None

                # Step 3: Fallback if no valid parse
                if not parsed:
                    return {
                        "project": project_name,
                        "summary": "Could not extract valid funding details.",
                        "details": {
                            "total_funding": None,
                            "last_round": None,
                            "investors": [],
                            "notable_backers": [],
                            "funding_sources": list(raw_sources.keys())
                        }
                    }

                # Step 4: Normalize numeric field (optional)
                details = parsed.get("details", {})
                if isinstance(details.get("total_funding"), str):
                    match = re.match(r"\$?(\d+(?:\.\d+)?)([MBmb]?)", details["total_funding"])
                    if match:
                        num, unit = match.groups()
                        multiplier = 1_000_000 if unit.lower() == "m" else 1_000_000_000 if unit.lower() == "b" else 1
                        details["total_funding_usd"] = float(num) * multiplier
                        parsed["details"] = details

                return parsed

        except Exception as e:
            logger.error(f"❌ Enhanced LLM funding extraction failed for {project_name}: {e}")
            return {
                "project": project_name,
                "summary": "Funding extraction failed due to an internal error.",
                "details": {
                    "total_funding": None,
                    "last_round": None,
                    "investors": [],
                    "notable_backers": [],
                    "funding_sources": list(raw_sources.keys())
                }
            }
