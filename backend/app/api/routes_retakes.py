from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import BestTakeRequest, BestTakeResponse
from app.services.gemini_service import select_best_take

router = APIRouter()


@router.post("/retakes/best", response_model=BestTakeResponse)
def retakes_best(request: BestTakeRequest) -> BestTakeResponse:
    try:
        return select_best_take(request.takes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

