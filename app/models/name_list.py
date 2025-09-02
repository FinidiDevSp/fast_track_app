from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class AllowedName(SQLModel, table=True):
    __tablename__ = "allowed_names"  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(sa_column=Column(String(150), unique=True, index=True, nullable=False))
    description: str = Field(sa_column=Column(String(200), nullable=False))


class BanName(SQLModel, table=True):
    __tablename__ = "ban_names"  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(sa_column=Column(String(150), unique=True, index=True, nullable=False))
    description: str = Field(sa_column=Column(String(200), nullable=False))
