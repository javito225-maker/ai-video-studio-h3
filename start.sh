#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
. .venv/bin/activate
exec uvicorn backend.main:app --host 127.0.0.1 --port 8787
