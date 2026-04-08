from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.models.schemas import (
    JobResponse,
    JobStepKey,
    OverallStatus,
    StepState,
)


@dataclass
class JobRecord:
    job_id: str
    user_id: str
    created_at: datetime
    overall_status: OverallStatus
    steps: dict[JobStepKey, StepState] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}

    def create_job(self, *, user_id: str) -> JobRecord:
        job_id = uuid.uuid4().hex
        created_at = datetime.now(timezone.utc)

        steps: dict[JobStepKey, StepState] = {
            "silence_removal": "pending",
            "best_take": "pending",
            "captions": "pending",
            "export": "pending",
        }

        record = JobRecord(
            job_id=job_id,
            user_id=user_id,
            created_at=created_at,
            overall_status="queued",
            steps=steps,
        )
        self._jobs[job_id] = record
        return record

    def get_job(self, *, job_id: str, user_id: str) -> JobRecord | None:
        record = self._jobs.get(job_id)
        if not record:
            return None
        if record.user_id != user_id:
            return None
        return record

    def to_response(self, record: JobRecord) -> JobResponse:
        return JobResponse(
            job_id=record.job_id,
            created_at=record.created_at.isoformat(),
            overall_status=record.overall_status,
            steps=record.steps,
            outputs=record.outputs,
        )


job_store = InMemoryJobStore()

