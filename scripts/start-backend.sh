#!/bin/bash
# Start backend development server (Flask)
set -e
cd "$(dirname "$0")/../api"

# Ensure a JWT secret is configured; the app refuses to start with a default/empty one.
export JWT_SECRET="${JWT_SECRET:-$(python3 -c 'import secrets; print(secrets.token_hex(32))')}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///./codesentinel_dev.db}"

FLASK_APP=src.app flask run --port 8000 --host 127.0.0.1
