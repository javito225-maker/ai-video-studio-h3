# AI Video Studio H3 — V1

Interface locale pour piloter MiniMax H3 open-source via ComfyUI, avec Ollama comme AI Director et FFmpeg pour l'assemblage.

## Cible
- Linux
- NVIDIA RTX 3090 24 GB
- 64 GB RAM
- ComfyUI local
- MiniMax H3 open-source
- Ollama + petit LLM local
- FFmpeg

## V1
1. Détection ComfyUI et Ollama
2. Création d'un projet vidéo
3. Découpage d'une idée en séquences via Ollama
4. Envoi d'un workflow API ComfyUI par séquence
5. Suivi de la file ComfyUI
6. Assemblage MP4 avec FFmpeg
7. Profils Draft / Balanced / Quality

## Installation
```bash
chmod +x install.sh start.sh
./install.sh
./start.sh
```

Ouvrir ensuite http://127.0.0.1:8787

## Important
Les workflows H3 exportés au format API doivent être placés dans `workflows/`. La V1 n'installe pas automatiquement les poids H3.
