# app/api/v1/routes.py
from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import create_user, list_users

api_router = APIRouter()


class Health(BaseModel):
    status: str


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


DBSession = Annotated[AsyncSession, Depends(get_db)]


@api_router.get("/health", response_model=Health)
async def health():
    return {"status": "ok"}


@api_router.post("/users", response_model=UserRead, status_code=201)
async def create_user_ep(payload: UserCreate, db: DBSession):
    return await create_user(db, payload.email, payload.full_name)


@api_router.get("/users", response_model=list[UserRead])
async def list_users_ep(db: DBSession):
    return await list_users(db)
