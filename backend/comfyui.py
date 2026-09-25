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
        self.base_url=base_url.rstrip("/"); self.client_id=str(uuid.uuid4())

    async def queue_workflow(self, workflow: dict):
        async with httpx.AsyncClient(timeout=60) as c:
            r=await c.post(f"{self.base_url}/prompt",json={"prompt":workflow,"client_id":self.client_id})
            if not r.is_success:
                raise RuntimeError(f"ComfyUI HTTP {r.status_code}: {r.text[:1500]}")
            return r.json()

    async def history(self,prompt_id:str):
        async with httpx.AsyncClient(timeout=30) as c:
            r=await c.get(f"{self.base_url}/history/{prompt_id}"); r.raise_for_status(); return r.json()

    @staticmethod
    def extract_outputs(entry:dict):
        found=[]
        for node_id,output in entry.get("outputs",{}).items():
            for key in ("videos","gifs","images","audio"):
                for item in output.get(key,[]) if isinstance(output,dict) else []:
                    if isinstance(item,dict) and item.get("filename"): found.append({"node":node_id,"type":key,**item})
        return found

def load_workflow(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def workflow_exists(path): return Path(path).is_file()

def build_h3_workflow(path,prompt,aspect_ratio="9:16",profile="Balanced",duration=15,seed=None):
    """Patch the exported MiniMax H3 T2V API workflow.

    The exported template uses ResolutionSelector for width/height links,
    PrimitiveFloat for seconds, and RandomNoise.noise_seed.
    """
    wf=copy.deepcopy(load_workflow(path))
    width,height=PROFILES.get(profile,PROFILES["Balanced"]).get(aspect_ratio,PROFILES["Balanced"]["9:16"])
    seconds=max(1,min(15,float(duration)))
    seed=seed if seed is not None else random.randint(0,2**31-1)
    changed={"prompt":0,"resolution":0,"duration":0,"seed":0}

    for node in wf.values():
        if not isinstance(node,dict): continue
        inputs=node.get("inputs")
        if not isinstance(inputs,dict): continue
        ctype=str(node.get("class_type","")).lower()

        # H3 conditioning node: prompt is direct, but resolution/length are links.
        if "minimaxh3" in ctype and "prompt" in inputs:
            inputs["prompt"]=prompt; changed["prompt"]+=1

        # Actual exported T2V template controls dimensions here.
        if ctype=="resolutionselector":
            inputs["aspect_ratio"]="9:16 (Portrait)" if aspect_ratio=="9:16" else "16:9 (Widescreen)"
            # Keep the template's megapixel target; ResolutionSelector calculates valid multiples.
            changed["resolution"]+=1

        # Actual exported T2V template controls duration in seconds here.
        if ctype=="primitivefloat" and ("duration" in str(node.get("_meta",{}).get("title","")).lower() or "value" in inputs):
            # Restrict this patch to PrimitiveFloat; the supplied workflow has the duration control here.
            inputs["value"]=seconds; changed["duration"]+=1

        if ctype=="randomnoise" and "noise_seed" in inputs:
            inputs["noise_seed"]=seed; changed["seed"]+=1
        elif "noise_seed" in inputs:
            inputs["noise_seed"]=seed; changed["seed"]+=1

    if not changed["prompt"]: raise ValueError("Aucun noeud MiniMax H3 avec entrée 'prompt' trouvé.")
    if not changed["resolution"]: raise ValueError("Aucun ResolutionSelector trouvé dans le workflow H3.")
    if not changed["duration"]: raise ValueError("Aucun contrôle de durée PrimitiveFloat trouvé dans le workflow H3.")

    # These are requested display dimensions; ComfyUI ResolutionSelector chooses its exact valid dimensions.
    return wf,{"width":width,"height":height,"duration":seconds,"fps":24,"seed":seed,"patched":changed}
