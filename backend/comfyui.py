import copy
import json
import random
import uuid
from pathlib import Path
import httpx

PROFILES = {
    "Draft": {"9:16": (448, 768), "16:9": (768, 448)},
    "Balanced": {"9:16": (576, 1024), "16:9": (1024, 576)},
    "Quality": {"9:16": (768, 1344), "16:9": (1344, 768)},
}

class ComfyUIClient:
    def __init__(self, base_url="http://127.0.0.1:8188"):
        self.base_url = base_url.rstrip("/")
        self.client_id = str(uuid.uuid4())

    async def queue_workflow(self, workflow: dict):
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(f"{self.base_url}/prompt", json={"prompt": workflow, "client_id": self.client_id})
            r.raise_for_status()
            return r.json()

    async def history(self, prompt_id: str):
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(f"{self.base_url}/history/{prompt_id}")
            r.raise_for_status()
            return r.json()

    @staticmethod
    def extract_outputs(entry: dict):
        found = []
        for node_id, output in entry.get("outputs", {}).items():
            for key in ("videos", "gifs", "images", "audio"):
                for item in output.get(key, []) if isinstance(output, dict) else []:
                    if isinstance(item, dict) and item.get("filename"):
                        found.append({"node": node_id, "type": key, **item})
        return found

def load_workflow(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def workflow_exists(path):
    return Path(path).is_file()

def _frames(seconds):
    target = max(5, min(362, round(seconds * 24)))
    values = list(range(5, 363, 17))
    return min(values, key=lambda x: abs(x-target))

def build_h3_workflow(path, prompt, aspect_ratio="9:16", profile="Balanced", duration=15, seed=None):
    wf = copy.deepcopy(load_workflow(path))
    width, height = PROFILES.get(profile, PROFILES["Balanced"]).get(aspect_ratio, PROFILES["Balanced"]["9:16"])
    length = _frames(duration)
    seed = seed if seed is not None else random.randint(0, 2**31-1)
    changed = {"prompt": 0, "resolution": 0, "length": 0, "seed": 0}

    # API-format workflow nodes are keyed by id and expose class_type + inputs.
    # We match official native H3 inputs by semantic field names instead of hard-coded node ids.
    for node in wf.values():
        if not isinstance(node, dict):
            continue
        inputs = node.get("inputs")
        if not isinstance(inputs, dict):
            continue
        ctype = str(node.get("class_type", "")).lower()
        if "minimaxh3" in ctype:
            if "prompt" in inputs:
                inputs["prompt"] = prompt; changed["prompt"] += 1
            if "width" in inputs and "height" in inputs:
                inputs["width"], inputs["height"] = width, height; changed["resolution"] += 1
            if "length" in inputs:
                inputs["length"] = length; changed["length"] += 1
        if "seed" in inputs and ("sampler" in ctype or "random" in ctype or "noise" in ctype):
            inputs["seed"] = seed; changed["seed"] += 1
        if "noise_seed" in inputs:
            inputs["noise_seed"] = seed; changed["seed"] += 1

    if not changed["prompt"]:
        raise ValueError("Aucun noeud MiniMax H3 avec entrée 'prompt' trouvé dans le workflow API.")
    return wf, {"width": width, "height": height, "frames": length, "fps": 24, "seed": seed, "patched": changed}
