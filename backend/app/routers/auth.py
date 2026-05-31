from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from ..core.security import create_access_token, verify_password
from ..dependencies import CurrentUser, DbSession
from ..models import User
from ..schemas.common import TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(db: DbSession, form: OAuth2PasswordRequestForm = Depends()):
    user = db.scalar(select(User).where(User.email == form.username))
    if not user or not verify_password(form.password, user.password_hash) or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
    return TokenOut(access_token=create_access_token(user.id, user.tenant_id))


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):
    return user
