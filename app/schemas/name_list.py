import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

Kind = Literal["allowlist", "denylist"]


class NameBase(BaseModel):
    slug: str = Field(max_length=150)
    description: str = Field(max_length=200)

    @field_validator("slug")
    @classmethod
    def normalize_and_validate_slug(cls, v: str) -> str:
        s = (v or "").strip().lower()
        if not s:
            raise ValueError("slug cannot be empty")
        if not re.fullmatch(r"[a-z0-9._-]+", s):
            raise ValueError("slug must match ^[a-z0-9-_.]+$")
        # prevent only dashes/underscores/dots
        if not re.search(r"[a-z0-9]", s):
            raise ValueError("slug must contain alphanumeric characters")
        return s


class NameCreate(NameBase):
    pass


class NameRead(NameBase):
    id: int


class NameUpdate(BaseModel):
    slug: Optional[str] = Field(default=None, max_length=150)
    description: Optional[str] = Field(default=None, max_length=200)

    @field_validator("slug")
    @classmethod
    def normalize_and_validate_slug_opt(cls, v: str | None) -> str | None:
        if v is None:
            return v
        s = v.strip().lower()
        if not s:
            raise ValueError("slug cannot be empty")
        if not re.fullmatch(r"[a-z0-9._-]+", s):
            raise ValueError("slug must match ^[a-z0-9-_.]+$")
        if not re.search(r"[a-z0-9]", s):
            raise ValueError("slug must contain alphanumeric characters")
        return s
