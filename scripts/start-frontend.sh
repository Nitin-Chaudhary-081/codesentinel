#!/bin/bash
# Start frontend development server
set -e
cd "$(dirname "$0")/../web"
npm install
npm run dev
