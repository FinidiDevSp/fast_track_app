from typing import Literal, Optional

from pydantic import BaseModel, Field

Kind = Literal["allowed", "ban"]


class NameBase(BaseModel):
    slug: str = Field(max_length=150)
    description: str = Field(max_length=200)


class NameCreate(NameBase):
    pass


class NameRead(NameBase):
    id: int


class NameUpdate(BaseModel):
    slug: Optional[str] = Field(default=None, max_length=150)
    description: Optional[str] = Field(default=None, max_length=200)
