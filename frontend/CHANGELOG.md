# Changelog

All notable changes to this frontend are documented here.

## 2026-04-03

- Video preview: resolve relative rough-cut URLs against the configured API base URL.

## 2026-04-05

- Upload page: load `localStorage` recents in `useEffect` so SSR/hydration match (fixes h2 “Recent jobs” mismatch).
- `next.config.ts`: set `turbopack.root` to `process.cwd()` to silence wrong inferred monorepo root.

- Removed Firecrawl placeholder button from upload page; theme comments updated (no style-crawl integration).

- Job page: show hint while silence-removal/transcription is running (model download + slow CPU).

## 2026-04-04

- Repo layout: app now lives under `Desktop/projects/shortcut/frontend` (monorepo with `backend/`). Run `npm install` here after copy (excluded `node_modules` from copy).

- API client: read `job_id` from `POST /jobs` (was incorrectly expecting `jobId`, which led to `/jobs/undefined/upload` and 404).
- API client: map `GET /jobs/{id}` snake_case fields (`job_id`, `created_at`, `overall_status`) to the frontend `Job` shape.
- Job page: show backend `outputs.error` and `outputs.error_export`; clearer status copy when export is skipped (e.g. FFmpeg missing).
