from fastapi import APIRouter, status

from ..core.crud import get_for_tenant, list_for_tenant
from ..dependencies import CurrentTenant, CurrentUser, DbSession
from ..models import Warehouse
from ..schemas.common import WarehouseCreate, WarehouseOut, WarehouseUpdate

router = APIRouter(prefix="/warehouses", tags=["warehouses"])


@router.get("", response_model=list[WarehouseOut])
def list_warehouses(tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return list_for_tenant(db, Warehouse, tenant.id)


@router.post("", response_model=WarehouseOut, status_code=status.HTTP_201_CREATED)
def create_warehouse(payload: WarehouseCreate, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    w = Warehouse(tenant_id=tenant.id, **payload.model_dump())
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


@router.get("/{warehouse_id}", response_model=WarehouseOut)
def get_warehouse(warehouse_id: int, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return get_for_tenant(db, Warehouse, tenant.id, warehouse_id)


@router.patch("/{warehouse_id}", response_model=WarehouseOut)
def update_warehouse(
    warehouse_id: int,
    payload: WarehouseUpdate,
    tenant: CurrentTenant,
    db: DbSession,
    _: CurrentUser,
):
    w = get_for_tenant(db, Warehouse, tenant.id, warehouse_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(w, k, v)
    db.commit()
    db.refresh(w)
    return w


@router.delete("/{warehouse_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warehouse(warehouse_id: int, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    w = get_for_tenant(db, Warehouse, tenant.id, warehouse_id)
    db.delete(w)
    db.commit()
