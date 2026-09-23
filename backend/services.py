import json, os, httpx
COMFY_URL=os.getenv("COMFY_URL","http://127.0.0.1:8188")
OLLAMA_URL=os.getenv("OLLAMA_URL","http://127.0.0.1:11434")

async def comfy_status():
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r=await c.get(f"{COMFY_URL}/system_stats")
            return {"online":r.is_success,"url":COMFY_URL}
    except Exception as e: return {"online":False,"url":COMFY_URL,"error":str(e)}

async def ollama_status():
    try:
        async with httpx.AsyncClient(timeout=3) as c:
            r=await c.get(f"{OLLAMA_URL}/api/tags"); data=r.json() if r.is_success else {}
            return {"online":r.is_success,"models":[m.get("name") for m in data.get("models",[])]}
    except Exception as e: return {"online":False,"error":str(e)}

async def plan_story(story,duration,sequence_seconds,model=None):
    count=max(1,duration//sequence_seconds)
    async with httpx.AsyncClient(timeout=10) as c:
        tr=await c.get(f"{OLLAMA_URL}/api/tags"); tr.raise_for_status(); tags=tr.json().get("models",[])
    names=[m.get("name") for m in tags if m.get("name")]
    if model and model in names: selected=model
    elif names: selected=names[0]
    else: raise RuntimeError("Ollama est en ligne mais aucun modèle n'est installé.")
    system=f"""You are the AI Director for MiniMax H3. Return ONLY valid JSON with a top-level sequences array. Create exactly {count} video sequences, maximum {sequence_seconds} seconds each. Every sequence: title, duration, prompt, characters, location, actions, camera, dialogue, sound. Keep character continuity. Never put production instructions inside dialogue."""
    payload={"model":selected,"stream":False,"format":"json","messages":[{"role":"system","content":system},{"role":"user","content":story}]}
    async with httpx.AsyncClient(timeout=180) as c:
        r=await c.post(f"{OLLAMA_URL}/api/chat",json=payload)
        if not r.is_success: raise RuntimeError(f"Ollama HTTP {r.status_code}: {r.text[:500]}")
        data=r.json(); raw=data.get("message",{}).get("content","")
    try: parsed=json.loads(raw)
    except json.JSONDecodeError as e: raise RuntimeError(f"Ollama n'a pas retourné du JSON valide: {raw[:500]}") from e
    if isinstance(parsed,list): parsed={"sequences":parsed}
    parsed["model_used"]=selected
    return parsed
