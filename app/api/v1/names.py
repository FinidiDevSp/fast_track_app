from typing import Annotated, AsyncGenerator, Literal

from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.schemas.name_list import Kind, NameCreate, NameRead, NameUpdate
from app.services.name_service import (
    create_name,
    delete_name,
    delete_name_by_slug,
    get_name,
    get_name_by_slug,
    import_folders_and_delete,
    list_names,
    update_name,
    update_name_by_slug,
)

router = APIRouter(prefix="/names", tags=["names"])


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


DBSession = Annotated[AsyncSession, Depends(get_db)]


class DeleteOK(BaseModel):
    ok: bool


@router.get("/{kind}", response_model=list[NameRead])
async def list_names_ep(
    kind: Kind,
    db: DBSession,
    q: str | None = Query(None, min_length=1, description="Buscar por slug o description"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    return await list_names(db, kind, q=q, offset=offset, limit=limit)


@router.post("/{kind}", response_model=NameRead, status_code=201)
async def create_name_ep(kind: Kind, payload: NameCreate, db: DBSession):
    return await create_name(db, kind, payload.slug, payload.description)


@router.get("/{kind}/{item_id}", response_model=NameRead)
async def get_name_ep(kind: Kind, db: DBSession, item_id: int = Path(..., ge=1)):
    return await get_name(db, kind, item_id)


@router.put("/{kind}/{item_id}", response_model=NameRead)
async def update_name_ep(kind: Kind, item_id: int, payload: NameUpdate, db: DBSession):
    return await update_name(db, kind, item_id, slug=payload.slug, description=payload.description)


@router.delete("/{kind}/{item_id}", response_model=DeleteOK)
async def delete_name_ep(kind: Kind, item_id: int, db: DBSession):
    await delete_name(db, kind, item_id)
    return {"ok": True}


# Slug-based endpoints (no necesidad de capturar IDs)
@router.get("/{kind}/slug/{slug}", response_model=NameRead)
async def get_name_by_slug_ep(kind: Kind, slug: str, db: DBSession):
    return await get_name_by_slug(db, kind, slug)


@router.put("/{kind}/slug/{slug}", response_model=NameRead)
async def update_name_by_slug_ep(kind: Kind, slug: str, payload: NameUpdate, db: DBSession):
    return await update_name_by_slug(
        db, kind, slug, new_slug=payload.slug, description=payload.description
    )


@router.delete("/{kind}/slug/{slug}", response_model=DeleteOK)
async def delete_name_by_slug_ep(kind: Kind, slug: str, db: DBSession):
    await delete_name_by_slug(db, kind, slug)
    return {"ok": True}


class ImportFoldersRequest(BaseModel):
    path: str = Field(min_length=1, description="Ruta absoluta o relativa a recorrer")


class ImportResult(BaseModel):
    ok: bool
    saved: int


def _normalize_kind(kind: str) -> Kind:
    k = kind.lower()
    return "allowed" if k in {"allow", "allowed"} else "ban"


@router.post("/import-folders/{kind}", response_model=ImportResult)
async def import_folders(
    kind: Literal["allow", "allowed", "ban"], payload: ImportFoldersRequest, db: DBSession
):
    norm = _normalize_kind(kind)
    saved = await import_folders_and_delete(db, norm, payload.path)
    return {"ok": True, "saved": saved}
