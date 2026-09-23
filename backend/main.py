from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .services import comfy_status, ollama_status, plan_story

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="AI Video Studio H3", version="1.0.0")

class PlanRequest(BaseModel):
    story: str
    duration: int = 60
    sequence_seconds: int = 15
    model: str = "llama3.1:8b-instruct-q4_K_M"

@app.get("/api/health")
async def health():
    return {
        "app": "ok",
        "comfyui": await comfy_status(),
        "ollama": await ollama_status(),
    }

@app.post("/api/plan")
async def plan(req: PlanRequest):
    if not req.story.strip():
        raise HTTPException(400, "Story is required")
    return await plan_story(req.story, req.duration, req.sequence_seconds, req.model)

app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")
