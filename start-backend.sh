#!/bin/sh
cd "$(dirname "$0")"
export PYTHONPATH=backend
exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
