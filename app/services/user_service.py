from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def create_user(db: AsyncSession, email: str, full_name: str) -> User:
    user = User(email=email, full_name=full_name)
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as err:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Email already exists") from err
    await db.refresh(user)
    return user


async def list_users(db: AsyncSession) -> Sequence[User]:
    res = await db.execute(select(User))
    return res.scalars().all()
