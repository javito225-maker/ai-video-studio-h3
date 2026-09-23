#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "=== AI Video Studio H3 V1 installer — Ubuntu 26.04 / Python 3.14 ==="

PYTHON=python3
command -v "$PYTHON" >/dev/null 2>&1 || {
  echo "Python 3 est requis."
  exit 1
}

ver=$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python détecté: $("$PYTHON" --version)"

command -v ffmpeg >/dev/null 2>&1 || {
  echo "Installation FFmpeg..."
  sudo apt-get update
  sudo apt-get install -y ffmpeg
}

if [ -d .venv ]; then
  echo "Suppression de l ancien environnement virtuel..."
  rm -rf .venv
fi

"$PYTHON" -m venv .venv
. .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

echo "Installation des dépendances binaires..."
python -m pip install --only-binary=:all: -r requirements.txt || {
  echo
  echo "ERREUR: une dépendance compatible avec Python $ver n a pas de wheel binaire."
  echo "Python utilisé: $(python --version)"
  echo "Pip utilisé: $(python -m pip --version)"
  exit 1
}

echo
echo "Vérification des imports..."
python - <<'PY'
import fastapi, uvicorn, httpx, pydantic
print("FastAPI:", fastapi.__version__)
print("Uvicorn:", uvicorn.__version__)
print("HTTPX:", httpx.__version__)
print("Pydantic:", pydantic.__version__)
PY

echo
echo "V1 installée avec succès."
echo "ComfyUI attendu: http://127.0.0.1:8188"
echo "Ollama attendu:  http://127.0.0.1:11434"
echo "Démarrage: ./start.sh"
