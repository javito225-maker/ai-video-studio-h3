import json
import uuid
from pathlib import Path
import httpx

class ComfyUIClient:
    def __init__(self, base_url="http://127.0.0.1:8188"):
        self.base_url = base_url.rstrip("/")
        self.client_id = str(uuid.uuid4())

    async def queue_workflow(self, workflow: dict):
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.post(f"{self.base_url}/prompt", json={
                "prompt": workflow,
                "client_id": self.client_id,
            })
            r.raise_for_status()
            return r.json()

    async def history(self, prompt_id: str):
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(f"{self.base_url}/history/{prompt_id}")
            r.raise_for_status()
            return r.json()

def load_workflow(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))
