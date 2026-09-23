#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

echo "=== AI Video Studio H3 V1 installer ==="

PYTHON=""
for candidate in python3.13 python3.12 python3.11 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    ver=$("$candidate" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    major=${ver%%.*}; minor=${ver##*.}
    if [ "$major" -eq 3 ] && [ "$minor" -ge 11 ] && [ "$minor" -le 13 ]; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  echo "Python 3.11, 3.12 ou 3.13 est requis pour cette V1."
  echo "Ton Python par défaut peut être 3.14; il ne sera pas utilisé pour le studio."
  echo "Installe Python 3.13 avec venv puis relance ./install.sh."
  exit 1
fi

echo "Python sélectionné: $PYTHON ($($PYTHON --version))"

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
python -m pip install --only-binary=:all: -r requirements.txt || {
  echo "Installation binaire impossible. Vérifie: .venv/bin/python --version"
  exit 1
}

echo "V1 installée avec succès."
echo "ComfyUI attendu: http://127.0.0.1:8188"
echo "Ollama attendu:  http://127.0.0.1:11434"
echo "Démarrage: ./start.sh"
