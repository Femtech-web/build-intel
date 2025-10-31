"""utils for the discovery providers."""

from urllib.parse import urlparse
import re


def refine_discovery(results: dict) -> dict:
    """
    Cross-refines discovery results by aligning across providers.
    Filters out irrelevant URLs (Twitter, Funding, Websites, Others)
    that do not correlate with discovered GitHub orgs, domains, or handles.
    """
    def clean_domain(url: str) -> str:
        try:
            d = urlparse(url).netloc.lower()
            d = re.sub(r"^www\.", "", d)
            d = d.split(":")[0]
            return d
        except Exception:
            return ""

    # 1️⃣ Collect trusted identifiers from all known sources
    trusted_tokens = set()

    # From websites + others
    for site in results.get("websites", []) + results.get("others", []):
        dom = clean_domain(site)
        if dom:
            for part in dom.split("."):
                if len(part) > 2 and part not in (
                    ".co", ".com", ".org", ".io", ".app", ".ai", ".net", ".xyz",
                      ".dev", ".tech", ".studio", ".systems", ".space", ".network",
                      ".cloud", ".tools", ".so", ".sh", ".gg", ".build",
                      ".eth", ".crypto", ".nft", ".dao", ".chain", ".sol", ".bnb"
                    ):
                    trusted_tokens.add(part)

    # From GitHub orgs
    for gh in results.get("githubs", []):
        parts = gh.split("/")
        if len(parts) >= 5:
            org = parts[3].lower()
            if len(org) > 2:
                trusted_tokens.add(org)

    # From Twitter handles
    for tw in results.get("twitters", []):
        match = re.search(r"x\.com/([A-Za-z0-9_-]+)", tw)
        if match:
            handle = match.group(1).lower()
            if len(handle) > 2:
                trusted_tokens.add(handle)

    # ✅ Add fuzzy matches (e.g., ourzora -> zora)
    extended_tokens = set(trusted_tokens)
    for token in trusted_tokens:
        if token.startswith("our") and len(token) > 4:
            extended_tokens.add(token[3:])
        elif token.endswith("labs") or token.endswith("protocol"):
            extended_tokens.add(token.replace("labs", "").replace("protocol", "").strip("-_"))
    trusted_tokens = extended_tokens

    # 2️⃣ Define helper to filter any list by token overlap
    def filter_urls(urls: list[str]) -> list[str]:
        refined = []
        for u in urls:
            low = u.lower()
            if any(tok in low for tok in trusted_tokens):
                refined.append(u)
        return refined

    # 3️⃣ Apply refinement to all key lists
    results["twitters"] = filter_urls(results.get("twitters", []))
    results["fundings"] = filter_urls(results.get("fundings", []))
    results["websites"] = filter_urls(results.get("websites", []))
    results["others"] = filter_urls(results.get("others", []))

    # 4️⃣ Deduplicate again (to be safe)
    for key in results.keys():
        if isinstance(results[key], list):
            results[key] = list(dict.fromkeys(results[key]))  # preserves order

    return results
