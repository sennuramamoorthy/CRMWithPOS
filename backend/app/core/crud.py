"""Tiny helpers that scope every query by tenant_id."""

from typing import TypeVar

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import Base

ModelT = TypeVar("ModelT", bound=Base)


def list_for_tenant(db: Session, model: type[ModelT], tenant_id: int) -> list[ModelT]:
    return list(
        db.scalars(
            select(model).where(model.tenant_id == tenant_id).order_by(model.id.desc())
        ).all()
    )


def get_for_tenant(db: Session, model: type[ModelT], tenant_id: int, obj_id: int) -> ModelT:
    obj = db.scalar(select(model).where(model.tenant_id == tenant_id, model.id == obj_id))
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"{model.__name__} not found")
    return obj
