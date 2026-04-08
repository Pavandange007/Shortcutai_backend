# Changelog

All notable changes to this backend are documented here.

## 2026-04-03

- Whisper: auto-fallback to CPU (`int8`) when CUDA is requested but unavailable.
- Pipeline: if caption grouping/persistence fails, mark job `failed` and stop early.
- Pipeline: if FFmpeg export fails (including missing `ffmpeg` on PATH), keep job `completed` and record `error_export` so transcript/captions remain usable.

## 2026-04-05

- Removed Firecrawl: deleted `firecrawl_service.py`, `routes_style`, `POST /style/sync`, `firecrawl-py` dependency, and `FIRECRAWL_API_KEY` from settings. Theming is manual via `frontend/tailwind.config.js` and `globals.css`.

- Whisper: log model load, transcribe start (file size), periodic segment progress, and total time so long CPU runs are visible in the terminal.

## 2026-04-04

- Project tree copied to `Desktop/projects/shortcut` (monorepo: `frontend/`, `backend/`); removed mistaken nested `backend/backend/` data mirror; added repo root `README.md`, `.gitignore`, and `backend/.env.example`.

- Pipeline: only start work when job status is `queued` (avoids duplicate concurrent runs).
- Pipeline: structured logging to stderr for start, success, transcript failures (`logger.exception`), and export warnings.
- `app.main`: attach `app.*` logger with INFO handler so pipeline logs show even if uvicorn log level is `warning`.
