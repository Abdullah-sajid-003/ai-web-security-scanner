# AI Web Security Scanner

A backend API that scans websites for common vulnerabilities and explains findings in plain English using AI.

## What it does

1. Users register and log in (JWT-based auth)
2. Users add "targets" — websites/hosts they own and want to scan
3. Launching a scan queues a background job that runs `nmap` against the target
4. Vulnerabilities found (e.g. open ports) are stored and listed per scan
5. Any vulnerability can be sent to an AI model for a plain-English explanation, remediation steps, and risk context

## Tech stack

- **API:** FastAPI
- **Database:** PostgreSQL (via SQLAlchemy + Alembic)
- **Background jobs:** Redis + RQ
- **Scanning:** nmap (via subprocess)
- **AI analysis:** Google Gemini API (free tier) — `gemini-3.5-flash-lite`

## Project structure
```
backend/
  app/
    api/routes/       # auth, targets, scans, vulnerabilities
    core/              # config, database, security, queue setup
    models/            # SQLAlchemy models
    schemas/            # Pydantic request/response schemas
    services/           # scanner.py (nmap), ai_analysis.py (Gemini)
  requirements.txt
frontend/
  app.py               # Streamlit UI
  venv/                # separate virtual environment for the frontend
scripts/
  00_setup_ubuntu.sh
  01_setup_python_env.sh
  02_setup_database.sh
  03_install_scan_tools.sh
  04_create_tables.py
  run_dev.sh           # starts the API server
  run_worker.sh        # starts the RQ background worker
  setup_all.sh
```
## Setup (first time)

```bash
./scripts/00_setup_ubuntu.sh
./scripts/01_setup_python_env.sh
./scripts/02_setup_database.sh
./scripts/03_install_scan_tools.sh
python3 scripts/04_create_tables.py
```

Then create your environment file:

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Fill in:
- `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY` — defaults usually work for local dev
- `GEMINI_API_KEY` — get a free key at https://aistudio.google.com/apikey

## Running the app

**This app requires TWO processes running at the same time**, in separate terminal tabs:

**Terminal 1 — API server:**
```bash
./scripts/run_dev.sh
```
Runs at `http://localhost:8000`. Interactive API docs at `http://localhost:8000/docs`.

**Terminal 2 — background worker:**
```bash
./scripts/run_worker.sh
```
This processes queued scans. **Scans will stay stuck in `queued` status forever if this isn't running.**

## Quick test / demo flow

```bash
# Register (first time only)
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"SecurePass123","full_name":"Your Name"}'

# Log in
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"SecurePass123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Add a target
curl -s -X POST http://localhost:8000/targets \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Nmap test host","url":"scanme.nmap.org"}'

# Launch a scan (replace TARGET_ID with the id returned above)
curl -s -X POST http://localhost:8000/targets/TARGET_ID/scans \
  -H "Authorization: Bearer $TOKEN"

# Check scan status (replace SCAN_ID with the id returned above)
curl -s http://localhost:8000/scans/SCAN_ID -H "Authorization: Bearer $TOKEN"

# Get AI explanation for a vulnerability (replace VULN_ID from the scan result)
curl -s -X POST http://localhost:8000/vulnerabilities/VULN_ID/analyze \
  -H "Authorization: Bearer $TOKEN"
```

## Notes

- Only scan hosts you own or have explicit permission to scan. `scanme.nmap.org` is intentionally provided by the nmap project for testing.
- AI analysis uses Gemini's free tier, which has request-rate limits — if you hit a quota error, wait a bit and retry.
- All targets/scans/vulnerabilities are scoped to the logged-in user.

## Frontend (Streamlit UI)

A simple web UI is available at `frontend/app.py`, built with Streamlit. It talks to the backend API over HTTP, so the backend (and CORS) must be running first.

**Important: the frontend uses its own separate Python virtual environment**, isolated from the backend's, because Streamlit and this version of FastAPI require conflicting versions of a shared dependency (`starlette`).

### First-time setup

```bash
python3 -m venv frontend/venv
source frontend/venv/bin/activate
pip install streamlit requests
```

### Running it

With the backend server and worker already running (see above), start the frontend in its own terminal tab:

```bash
cd ~/ai-web-security-scanner
source frontend/venv/bin/activate
streamlit run frontend/app.py
```

Then open `http://localhost:8501` in your browser. Log in (or register), add a target, launch a scan, and click "AI Analyze" on any vulnerability to see the AI-generated explanation.

### Running everything together

This project now needs **three processes running at once**, each in its own terminal tab:

1. `./scripts/run_dev.sh` — backend API (port 8000)
2. `./scripts/run_worker.sh` — background scan worker
3. `streamlit run frontend/app.py` (with `frontend/venv` activated) — web UI (port 8501)

Tip: rename your terminal tabs (most terminal apps support this) so it's easy to tell which one is running what.
