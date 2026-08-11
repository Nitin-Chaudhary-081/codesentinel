#!/bin/bash
# Run all tests with coverage
set -e
echo "=== Backend Tests ==="
cd "$(dirname "$0")/../api"
source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt --quiet
pytest --cov=src --cov-report=term-missing

echo ""
echo "=== Frontend Tests ==="
cd "$(dirname "$0")/../web"
npm ci --silent
npm test -- --coverage
