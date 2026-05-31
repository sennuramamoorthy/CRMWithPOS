from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from ..core.crud import get_for_tenant, list_for_tenant
from ..dependencies import CurrentTenant, CurrentUser, DbSession
from ..models import Invoice, Order, OrderItem, Product, StockLevel, Warehouse
from ..schemas.common import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])


def _gen_code(prefix: str, obj_id: int) -> str:
    ts = datetime.now(timezone.utc).strftime("%y%m%d")
    return f"{prefix}-{ts}-{obj_id:05d}"


@router.get("", response_model=list[OrderOut])
def list_orders(tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return list_for_tenant(db, Order, tenant.id)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return get_for_tenant(db, Order, tenant.id, order_id)


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, tenant: CurrentTenant, db: DbSession, user: CurrentUser):
    if not payload.items:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "order must have at least one item")

    # Validate warehouse
    get_for_tenant(db, Warehouse, tenant.id, payload.warehouse_id)

    subtotal = Decimal("0")
    items: list[OrderItem] = []

    for item in payload.items:
        product = get_for_tenant(db, Product, tenant.id, item.product_id)
        unit_price = item.unit_price if item.unit_price is not None else product.price
        line_total = unit_price * item.quantity
        subtotal += line_total

        # Deduct stock for the chosen warehouse
        level = db.scalar(
            select(StockLevel).where(
                StockLevel.tenant_id == tenant.id,
                StockLevel.warehouse_id == payload.warehouse_id,
                StockLevel.product_id == product.id,
            )
        )
        on_hand = level.quantity if level else 0
        if on_hand < item.quantity:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"insufficient stock for {product.sku}: have {on_hand}, need {item.quantity}",
            )
        level.quantity -= item.quantity  # type: ignore[union-attr]

        items.append(
            OrderItem(
                tenant_id=tenant.id,
                product_id=product.id,
                quantity=item.quantity,
                unit_price=unit_price,
                line_total=line_total,
            )
        )

    total = subtotal + payload.tax - payload.discount
    order = Order(
        tenant_id=tenant.id,
        code="PENDING",
        customer_id=payload.customer_id,
        warehouse_id=payload.warehouse_id,
        status="confirmed",
        subtotal=subtotal,
        tax=payload.tax,
        discount=payload.discount,
        total=total,
        created_by=user.id,
        items=items,
    )
    db.add(order)
    db.flush()  # need order.id for code + invoice
    order.code = _gen_code("ORD", order.id)

    invoice = Invoice(
        tenant_id=tenant.id,
        number=_gen_code("INV", order.id),
        order_id=order.id,
        customer_id=payload.customer_id,
        total=total,
        amount_paid=Decimal("0"),
        status="unpaid" if total > 0 else "paid",
    )
    db.add(invoice)
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    order = get_for_tenant(db, Order, tenant.id, order_id)
    if order.status == "cancelled":
        return order

    # Return stock
    for item in order.items:
        level = db.scalar(
            select(StockLevel).where(
                StockLevel.tenant_id == tenant.id,
                StockLevel.warehouse_id == order.warehouse_id,
                StockLevel.product_id == item.product_id,
            )
        )
        if level is None:
            level = StockLevel(
                tenant_id=tenant.id,
                warehouse_id=order.warehouse_id,
                product_id=item.product_id,
                quantity=0,
            )
            db.add(level)
        level.quantity += item.quantity

    order.status = "cancelled"
    # Void the invoice
    invoice = db.scalar(select(Invoice).where(Invoice.order_id == order.id))
    if invoice is not None:
        invoice.status = "void"

    db.commit()
    db.refresh(order)
    return order
