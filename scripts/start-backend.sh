#!/bin/bash
# Start backend development server
set -e
cd "$(dirname "$0")/../api"
source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt --quiet
uvicorn src.main:app --reload --port 8000
