from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["v1"])

@router.get("/health")
def health() -> dict:
    return {"status": "ok"}

@router.get("/version")
def version() -> dict:
    return {"version": "v1"}
