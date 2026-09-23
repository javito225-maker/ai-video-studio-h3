import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .services import comfy_status, ollama_status, plan_story
from .comfyui import ComfyUIClient, build_h3_workflow, workflow_exists

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / "workflows" / "h3_t2v.json"
app = FastAPI(title="AI Video Studio H3", version="1.1.1")
comfy = ComfyUIClient(os.getenv("COMFY_URL", "http://127.0.0.1:8188"))

class PlanRequest(BaseModel):
    story: str
    duration: int = 60
    sequence_seconds: int = 15
    model: str | None = None

class GenerateRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "9:16"
    profile: str = "Balanced"
    duration: int = 15
    seed: int | None = None

@app.exception_handler(Exception)
async def json_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"detail": str(exc), "type": exc.__class__.__name__})

@app.get("/api/health")
async def health():
    return {"app":"ok","comfyui":await comfy_status(),"ollama":await ollama_status(),"h3_workflow":workflow_exists(WORKFLOW)}

@app.post("/api/plan")
async def plan(req: PlanRequest):
    if not req.story.strip():
        raise HTTPException(400, "Story is required")
    try:
        return await plan_story(req.story, req.duration, req.sequence_seconds, req.model)
    except Exception as e:
        raise HTTPException(502, f"AI Director/Ollama: {e}")

@app.post("/api/generate")
async def generate(req: GenerateRequest):
    if not req.prompt.strip(): raise HTTPException(400, "Prompt is required")
    if not workflow_exists(WORKFLOW): raise HTTPException(503, "Workflow H3 absent.")
    try:
        workflow, meta = build_h3_workflow(WORKFLOW, req.prompt, req.aspect_ratio, req.profile, req.duration, req.seed)
        queued = await comfy.queue_workflow(workflow)
        return {"ok":True,"prompt_id":queued.get("prompt_id"),"meta":meta}
    except Exception as e:
        raise HTTPException(502, f"ComfyUI/H3: {e}")

@app.get("/api/jobs/{prompt_id}")
async def job(prompt_id: str):
    try:
        data=await comfy.history(prompt_id); entry=data.get(prompt_id)
        if not entry: return {"status":"queued_or_running","prompt_id":prompt_id}
        return {"status":"completed","prompt_id":prompt_id,"outputs":comfy.extract_outputs(entry)}
    except Exception as e:
        raise HTTPException(502, f"ComfyUI: {e}")

app.mount("/", StaticFiles(directory=ROOT/"frontend", html=True), name="frontend")
