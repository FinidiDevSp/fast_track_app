from typing import Optional

from sqlmodel import Field, SQLModel


class AllowedName(SQLModel, table=True):
    __tablename__ = "allowed_names"  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(max_length=150, index=True, unique=True)
    description: str = Field(max_length=200)


class BanName(SQLModel, table=True):
    __tablename__ = "ban_names"  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(max_length=150, index=True, unique=True)
    description: str = Field(max_length=200)
