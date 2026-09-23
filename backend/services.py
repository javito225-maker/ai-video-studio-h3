import json
import os
import httpx

COMFY_URL = os.getenv("COMFY_URL", "http://127.0.0.1:8188")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

async def comfy_status():
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r = await c.get(f"{COMFY_URL}/system_stats")
            return {"online": r.is_success, "url": COMFY_URL}
    except Exception as e:
        return {"online": False, "url": COMFY_URL, "error": str(e)}

async def ollama_status():
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r = await c.get(f"{OLLAMA_URL}/api/tags")
            data = r.json() if r.is_success else {}
            return {"online": r.is_success, "models": [m.get("name") for m in data.get("models", [])]}
    except Exception as e:
        return {"online": False, "error": str(e)}

async def plan_story(story, duration, sequence_seconds, model):
    count = max(1, duration // sequence_seconds)
    system = f"""You are the AI Director for MiniMax H3.
Return ONLY valid JSON.
Create exactly {count} video sequences, maximum {sequence_seconds} seconds each.
For every sequence include: title, duration, prompt, characters, location, actions, camera, dialogue, sound.
Prompts must describe visible actions precisely and keep character continuity.
Do not put production instructions inside dialogue."""
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": story},
        ],
    }
    async with httpx.AsyncClient(timeout=180) as c:
        r = await c.post(f"{OLLAMA_URL}/api/chat", json=payload)
        r.raise_for_status()
        raw = r.json()["message"]["content"]
        return json.loads(raw)
