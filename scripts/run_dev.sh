#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    echo "No venv found. Run scripts/01_setup_python_env.sh first." >&2
    exit 1
fi
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
