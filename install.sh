#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo "Python3 requis"; exit 1; }
command -v ffmpeg >/dev/null || { echo "Installation FFmpeg..."; sudo apt-get update && sudo apt-get install -y ffmpeg; }
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "V1 installée."
echo "Assure-toi que ComfyUI écoute sur 127.0.0.1:8188 et Ollama sur 127.0.0.1:11434."
echo "Puis: ./start.sh"
