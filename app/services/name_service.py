import os
import shutil
from typing import Literal, Sequence, Type

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.name_list import AllowedName, BanName

Kind = Literal["allowed", "ban"]


def _model_for(kind: Kind) -> Type[AllowedName] | Type[BanName]:
    return AllowedName if kind == "allowed" else BanName


async def list_names(
    db: AsyncSession,
    kind: Kind,
    q: str | None = None,
    *,
    offset: int = 0,
    limit: int = 50,
) -> Sequence[AllowedName] | Sequence[BanName]:
    Model = _model_for(kind)
    stmt = select(Model)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Model.slug.ilike(like), Model.description.ilike(like)))  # type: ignore[attr-defined]
    stmt = stmt.order_by(Model.id).offset(offset).limit(limit)
    res = await db.execute(stmt)
    return res.scalars().all()


async def get_name(db: AsyncSession, kind: Kind, item_id: int) -> AllowedName | BanName:
    Model = _model_for(kind)
    obj = await db.get(Model, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return obj


async def create_name(
    db: AsyncSession, kind: Kind, slug: str, description: str
) -> AllowedName | BanName:
    Model = _model_for(kind)
    obj = Model(slug=slug, description=description)  # type: ignore[call-arg]
    db.add(obj)
    try:
        await db.commit()
    except IntegrityError as err:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Slug already exists") from err
    await db.refresh(obj)
    return obj


async def update_name(
    db: AsyncSession, kind: Kind, item_id: int, *, slug: str | None, description: str | None
) -> AllowedName | BanName:
    obj = await get_name(db, kind, item_id)
    changed = False
    if slug is not None:
        obj.slug = slug  # type: ignore[assignment]
        changed = True
    if description is not None:
        obj.description = description  # type: ignore[assignment]
        changed = True
    if not changed:
        return obj
    try:
        await db.commit()
    except IntegrityError as err:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Slug already exists") from err
    await db.refresh(obj)
    return obj


async def delete_name(db: AsyncSession, kind: Kind, item_id: int) -> None:
    obj = await get_name(db, kind, item_id)
    await db.delete(obj)
    await db.commit()


# Slug- based helpers (avoid needing IDs)
async def get_name_by_slug(db: AsyncSession, kind: Kind, slug: str) -> AllowedName | BanName:
    Model = _model_for(kind)
    res = await db.execute(select(Model).where(Model.slug == slug))  # type: ignore[attr-defined]
    obj = res.scalars().first()
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return obj


async def update_name_by_slug(
    db: AsyncSession, kind: Kind, slug: str, *, new_slug: str | None, description: str | None
) -> AllowedName | BanName:
    obj = await get_name_by_slug(db, kind, slug)
    changed = False
    if new_slug is not None:
        obj.slug = new_slug  # type: ignore[assignment]
        changed = True
    if description is not None:
        obj.description = description  # type: ignore[assignment]
        changed = True
    if not changed:
        return obj
    try:
        await db.commit()
    except IntegrityError as err:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Slug already exists") from err
    await db.refresh(obj)
    return obj


async def delete_name_by_slug(db: AsyncSession, kind: Kind, slug: str) -> None:
    obj = await get_name_by_slug(db, kind, slug)
    await db.delete(obj)
    await db.commit()


async def import_folders_and_delete(db: AsyncSession, kind: Kind, root_path: str) -> int:
    """Traverse `root_path`, collect folder names, upsert into table, then delete those folders.

    Returns the number of records saved/updated.
    """
    if not os.path.exists(root_path) or not os.path.isdir(root_path):
        raise HTTPException(status_code=400, detail="Path does not exist or is not a directory")

    # Map slug -> list of absolute folder paths with that name
    slug_to_paths: dict[str, list[str]] = {}
    for current, dirs, _files in os.walk(root_path):
        for d in dirs:
            slug = d
            abs_path = os.path.join(current, d)
            slug_to_paths.setdefault(slug, []).append(abs_path)

    if not slug_to_paths:
        return 0

    Model = _model_for(kind)

    # Fetch existing slugs
    slugs = list(slug_to_paths.keys())
    res = await db.execute(select(Model).where(Model.slug.in_(slugs)))  # type: ignore[attr-defined]
    existing_by_slug = {obj.slug: obj for obj in res.scalars().all()}  # type: ignore[attr-defined]

    saved = 0
    # Upsert
    for slug in slugs:
        description = f"Imported from {root_path}"
        if slug in existing_by_slug:
            obj = existing_by_slug[slug]
            # Update description if different
            if getattr(obj, "description", None) != description:
                obj.description = description  # type: ignore[assignment]
                saved += 1
        else:
            obj = Model(slug=slug, description=description)  # type: ignore[call-arg]
            db.add(obj)
            saved += 1

    await db.commit()

    # Delete directories collected
    # Only delete paths under the provided root_path to be safe.
    for paths in slug_to_paths.values():
        for p in paths:
            try:
                # Safety: ensure path startswith root_path
                rp = os.path.realpath(root_path)
                pp = os.path.realpath(p)
                if pp.startswith(rp):
                    shutil.rmtree(pp, ignore_errors=True)
            except Exception:
                # Ignore individual deletion errors; continue with others
                pass

    return saved
