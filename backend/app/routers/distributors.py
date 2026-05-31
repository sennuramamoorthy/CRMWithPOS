from fastapi import APIRouter, status

from ..core.crud import get_for_tenant, list_for_tenant
from ..dependencies import CurrentTenant, CurrentUser, DbSession
from ..models import Distributor
from ..schemas.common import DistributorCreate, DistributorOut, DistributorUpdate

router = APIRouter(prefix="/distributors", tags=["distributors"])


@router.get("", response_model=list[DistributorOut])
def list_distributors(tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return list_for_tenant(db, Distributor, tenant.id)


@router.post("", response_model=DistributorOut, status_code=status.HTTP_201_CREATED)
def create_distributor(payload: DistributorCreate, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    d = Distributor(tenant_id=tenant.id, **payload.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


@router.get("/{distributor_id}", response_model=DistributorOut)
def get_distributor(distributor_id: int, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return get_for_tenant(db, Distributor, tenant.id, distributor_id)


@router.patch("/{distributor_id}", response_model=DistributorOut)
def update_distributor(
    distributor_id: int,
    payload: DistributorUpdate,
    tenant: CurrentTenant,
    db: DbSession,
    _: CurrentUser,
):
    d = get_for_tenant(db, Distributor, tenant.id, distributor_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(d, k, v)
    db.commit()
    db.refresh(d)
    return d


@router.delete("/{distributor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_distributor(distributor_id: int, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    d = get_for_tenant(db, Distributor, tenant.id, distributor_id)
    db.delete(d)
    db.commit()
