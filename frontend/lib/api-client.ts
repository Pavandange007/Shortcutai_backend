import type { Job, JobOverallStatus, JobStepKey, StepState } from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const AUTH_TOKEN_KEY = "shotcut_ai_auth_token_v1";

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

export type CreateJobResponse = {
  jobId: string;
};

/** FastAPI/Pydantic JSON uses snake_case for top-level job fields. */
interface JobApiPayload {
  job_id: string;
  created_at: string;
  overall_status: JobOverallStatus;
  steps: Record<JobStepKey, StepState>;
  outputs?: Record<string, unknown>;
}

function mapJobPayload(data: JobApiPayload): Job {
  return {
    id: data.job_id,
    createdAt: data.created_at,
    overallStatus: data.overall_status,
    steps: data.steps,
    outputs: data.outputs as Job["outputs"] | undefined,
  };
}

async function parseJson<T>(res: Response): Promise<T> {
  const text = await res.text();
  if (!res.ok) {
    throw new Error(
      `Request failed (${res.status}): ${text || res.statusText}`,
    );
  }
  return (text ? JSON.parse(text) : ({} as T)) as T;
}

let authTokenCache: string | null | undefined = undefined;
let authTokenPromise: Promise<string | null> | null = null;

async function ensureAuthToken(): Promise<string | null> {
  if (authTokenCache !== undefined) return authTokenCache;
  if (authTokenPromise) return authTokenPromise;

  authTokenPromise = (async () => {
    if (typeof window === "undefined") return null;

    const existing = window.localStorage.getItem(AUTH_TOKEN_KEY);
    if (existing) {
      authTokenCache = existing;
      return existing;
    }

    const res = await fetch(`${API_BASE_URL}/auth/session`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    const data = await parseJson<{ token: string }>(res);
    window.localStorage.setItem(AUTH_TOKEN_KEY, data.token);
    authTokenCache = data.token;
    return data.token;
  })();

  try {
    return await authTokenPromise;
  } finally {
    authTokenPromise = null;
  }
}

async function authedFetch(
  url: string,
  init: RequestInit,
): Promise<Response> {
  const token = await ensureAuthToken();
  const headers = new Headers(init.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  return fetch(url, { ...init, headers });
}

export async function createJob(): Promise<CreateJobResponse> {
  const res = await authedFetch(`${API_BASE_URL}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  const data = await parseJson<{ job_id: string }>(res);
  return { jobId: data.job_id };
}

export async function uploadVideo(jobId: string, file: File): Promise<void> {
  const form = new FormData();
  form.append("file", file);

  const res = await authedFetch(`${API_BASE_URL}/jobs/${jobId}/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Upload failed (${res.status}): ${text}`);
  }
}

export async function getJobStatus(jobId: string): Promise<Job> {
  const res = await authedFetch(`${API_BASE_URL}/jobs/${jobId}`, {
    method: "GET",
  });
  const data = await parseJson<JobApiPayload>(res);
  return mapJobPayload(data);
}

