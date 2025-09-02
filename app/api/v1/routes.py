"""API root router for v1."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.v1.names import router as names_router

api_router = APIRouter()


class Health(BaseModel):
    status: str


@api_router.get(
    "/health",
    response_model=Health,
    response_model_exclude_none=True,
    tags=["system"],
    summary="Health check",
    description="Simple endpoint to verify the API is up.",
)
async def health():
    return {"status": "ok"}


# Mount names endpoints
api_router.include_router(names_router)
