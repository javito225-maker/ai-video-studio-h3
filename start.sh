#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  echo "AI Video Studio H3 n est pas installé correctement."
  echo "Exécute d abord: ./install.sh"
  exit 1
fi

HOST="${H3_HOST:-0.0.0.0}"
PORT="${H3_PORT:-8787}"

echo "=== AI Video Studio H3 ==="
echo "Écoute réseau: ${HOST}:${PORT}"
echo "Accès LAN/externe: http://ADRESSE_IP_DU_SERVEUR:${PORT}"

exec .venv/bin/python -m uvicorn backend.main:app --host "$HOST" --port "$PORT"
