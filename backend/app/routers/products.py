from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from ..core.crud import get_for_tenant, list_for_tenant
from ..dependencies import CurrentTenant, CurrentUser, DbSession
from ..models import Product, StockLevel, Warehouse
from ..schemas.common import (
    ProductCreate,
    ProductOut,
    ProductUpdate,
    StockAdjust,
    StockLevelOut,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return list_for_tenant(db, Product, tenant.id)


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    p = Product(tenant_id=tenant.id, **payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return get_for_tenant(db, Product, tenant.id, product_id)


@router.patch("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    payload: ProductUpdate,
    tenant: CurrentTenant,
    db: DbSession,
    _: CurrentUser,
):
    p = get_for_tenant(db, Product, tenant.id, product_id)
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    p = get_for_tenant(db, Product, tenant.id, product_id)
    db.delete(p)
    db.commit()


# ---------- stock levels ----------

@router.get("/stock/levels", response_model=list[StockLevelOut])
def list_stock(tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return list(
        db.scalars(
            select(StockLevel).where(StockLevel.tenant_id == tenant.id).order_by(StockLevel.id.desc())
        ).all()
    )


@router.post("/stock/adjust", response_model=StockLevelOut)
def adjust_stock(payload: StockAdjust, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    # Verify warehouse + product belong to tenant
    get_for_tenant(db, Warehouse, tenant.id, payload.warehouse_id)
    get_for_tenant(db, Product, tenant.id, payload.product_id)

    level = db.scalar(
        select(StockLevel).where(
            StockLevel.tenant_id == tenant.id,
            StockLevel.warehouse_id == payload.warehouse_id,
            StockLevel.product_id == payload.product_id,
        )
    )
    if level is None:
        level = StockLevel(
            tenant_id=tenant.id,
            warehouse_id=payload.warehouse_id,
            product_id=payload.product_id,
            quantity=max(0, payload.delta),
        )
        db.add(level)
    else:
        new_qty = level.quantity + payload.delta
        if new_qty < 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "stock cannot go negative")
        level.quantity = new_qty

    db.commit()
    db.refresh(level)
    return level
