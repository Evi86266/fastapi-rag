"""区分进程存活与问答链路就绪。"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={"status": "not_ready", "reason": "问答链路尚未接入"},
    )
