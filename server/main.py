
from dotenv import load_dotenv # type: ignore
load_dotenv() 

from fastapi import FastAPI, HTTPException   # type: ignore # noqa: E402
from fastapi.middleware.cors import CORSMiddleware # type: ignore  # noqa: E402
from pydantic import BaseModel  # type: ignore # noqa: E402
from src.agent import BuildIntelAgent  # noqa: E402


app = FastAPI(title="BuildIntel API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    project_name: str

@app.post("/analyze")
async def analyze_project(request: AnalyzeRequest):
    try:
        agent = BuildIntelAgent()
        await agent.setup()
        result = await agent.analyze_project(request.project_name)
        data = result.get("RESULT", {}).get("content", result)
        return {"status": "success", "data": data}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

