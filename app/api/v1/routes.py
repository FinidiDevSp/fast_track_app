"""API root router for v1."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.api.v1.names import router as names_router

api_router = APIRouter()


class Health(BaseModel):
    status: str


@api_router.get("/health", response_model=Health)
async def health():
    return {"status": "ok"}


# Mount names endpoints
api_router.include_router(names_router)
