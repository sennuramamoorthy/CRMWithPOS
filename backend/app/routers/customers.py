from fastapi import APIRouter, status

from ..core.crud import get_for_tenant, list_for_tenant
from ..dependencies import CurrentTenant, CurrentUser, DbSession
from ..models import Customer
from ..schemas.common import CustomerCreate, CustomerOut, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerOut])
def list_customers(tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return list_for_tenant(db, Customer, tenant.id)


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    c = Customer(tenant_id=tenant.id, **payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return get_for_tenant(db, Customer, tenant.id, customer_id)


@router.patch("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    tenant: CurrentTenant,
    db: DbSession,
    _: CurrentUser,
):
    c = get_for_tenant(db, Customer, tenant.id, customer_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    c = get_for_tenant(db, Customer, tenant.id, customer_id)
    db.delete(c)
    db.commit()
