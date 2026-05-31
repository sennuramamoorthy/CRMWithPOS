from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from ..core.security import hash_password
from ..dependencies import CurrentTenant, CurrentUser, DbSession, RequireAdmin
from ..models import User
from ..schemas.common import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return db.scalars(select(User).where(User.tenant_id == tenant.id).order_by(User.id)).all()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, tenant: CurrentTenant, db: DbSession, _: RequireAdmin):
    exists = db.scalar(
        select(User).where(User.tenant_id == tenant.id, User.email == payload.email)
    )
    if exists:
        raise HTTPException(status.HTTP_409_CONFLICT, "email already exists")
    user = User(
        tenant_id=tenant.id,
        email=payload.email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
