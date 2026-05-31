import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from ..config import settings
from ..dependencies import CurrentTenant, DbSession, RequireAdmin
from ..schemas.common import TenantOut, TenantUpdate

router = APIRouter(prefix="/tenant", tags=["tenant"])

ALLOWED_LOGO_EXT = {".png", ".jpg", ".jpeg", ".svg", ".webp"}


@router.get("", response_model=TenantOut)
def get_tenant(tenant: CurrentTenant):
    return tenant


@router.patch("", response_model=TenantOut)
def update_tenant(
    payload: TenantUpdate,
    tenant: CurrentTenant,
    db: DbSession,
    _: RequireAdmin,
):
    if payload.name is not None:
        tenant.name = payload.name
    if payload.primary_color is not None:
        tenant.primary_color = payload.primary_color
    db.commit()
    db.refresh(tenant)
    return tenant


@router.post("/logo", response_model=TenantOut)
def upload_logo(
    tenant: CurrentTenant,
    db: DbSession,
    _: RequireAdmin,
    file: UploadFile = File(...),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_LOGO_EXT:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"unsupported file type {ext}")

    upload_dir = Path(settings.upload_dir) / "logos"
    upload_dir.mkdir(parents=True, exist_ok=True)
    fname = f"tenant-{tenant.id}-{uuid.uuid4().hex}{ext}"
    dest = upload_dir / fname
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    tenant.logo_url = f"/uploads/logos/{fname}"
    db.commit()
    db.refresh(tenant)
    return tenant
