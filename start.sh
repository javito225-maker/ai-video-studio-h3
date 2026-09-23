#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  echo "AI Video Studio H3 n est pas installé correctement."
  echo "Exécute d abord: ./install.sh"
  exit 1
fi

exec .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8787
