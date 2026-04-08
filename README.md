# Shortcut — AI Video Editor MVP

Monorepo layout:

- **`frontend/`** — Next.js (App Router) upload UI and job status.
- **`backend/`** — FastAPI, faster-whisper, Gemini, FFmpeg pipeline.

## How it works

1. **Browser** — User opens the Next.js app, gets a JWT via `POST /auth/session`, then `POST /jobs` and `POST /jobs/{id}/upload` with the video file.
2. **Background pipeline** (`app/workers/background.py`) runs after upload: **faster-whisper** produces word-level timestamps → **silence heuristics** build `timeline.json` → optional **Gemini** “best take” copy on the single transcript → **caption** lines + optional FFmpeg **burn-in** → FFmpeg **rough cut** from kept timeline segments (needs `ffmpeg` on `PATH`).
3. **Storage** — Files live under `backend/data/uploads/{user_id}/{job_id}/` (video, JSON artifacts). Jobs are tracked in an in-memory store (MVP).
4. **Frontend** — `/upload` creates the job and uploads; `/jobs/[jobId]` polls `GET /jobs/{id}` until steps complete and shows preview URL when export succeeds.

Optional: **`GEMINI_API_KEY`** improves best-take text; without it the pipeline still defaults sensibly. **FFmpeg** is required for burned captions and rough-cut MP4 export.

## Prerequisites

- Node.js 20+ (for frontend)
- Python 3.10+ (for backend)
- **FFmpeg** on `PATH` (rough cut export and caption burn-in)
- Optional: CUDA for faster-whisper (`GPU_DEVICE`)

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# edit .env — set AUTH_SECRET (32+ chars), API keys as needed
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend

```powershell
cd frontend
npm install
# optional: set API URL
# $env:NEXT_PUBLIC_API_BASE_URL="http://127.0.0.1:8000"
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). The UI defaults the API to `http://localhost:8000`.

## Environment

See `backend/.env.example`. Never commit real `.env` files.

## Changelogs

- `frontend/CHANGELOG.md`
- `backend/CHANGELOG.md`
