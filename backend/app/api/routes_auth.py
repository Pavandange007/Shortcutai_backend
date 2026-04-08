from __future__ import annotations

from pydantic import BaseModel
from fastapi import APIRouter

from app.services.auth_service import issue_session

router = APIRouter()


class SessionResponse(BaseModel):
    user_id: str
    token: str


@router.post("/auth/session", response_model=SessionResponse)
def create_session() -> SessionResponse:
    user_id, token = issue_session()
    return SessionResponse(user_id=user_id, token=token)

