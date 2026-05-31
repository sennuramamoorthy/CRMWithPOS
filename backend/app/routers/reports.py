from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter
from sqlalchemy import func, select

from ..dependencies import CurrentTenant, CurrentUser, DbSession
from ..models import (
    Customer,
    Distributor,
    Invoice,
    Order,
    Product,
    StockLevel,
    Warehouse,
)
from ..schemas.common import DailyRevenuePoint, ReportSummary

LOW_STOCK_THRESHOLD = 5

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary", response_model=ReportSummary)
def summary(tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    tid = tenant.id
    since = datetime.now(timezone.utc) - timedelta(days=30)

    def count(model) -> int:  # type: ignore[no-untyped-def]
        return db.scalar(select(func.count()).select_from(model).where(model.tenant_id == tid)) or 0

    revenue_30d = db.scalar(
        select(func.coalesce(func.sum(Order.total), 0))
        .where(Order.tenant_id == tid, Order.status != "cancelled", Order.created_at >= since)
    ) or Decimal("0")

    orders_30d = db.scalar(
        select(func.count())
        .select_from(Order)
        .where(Order.tenant_id == tid, Order.status != "cancelled", Order.created_at >= since)
    ) or 0

    outstanding = db.scalar(
        select(func.coalesce(func.sum(Invoice.total - Invoice.amount_paid), 0))
        .where(Invoice.tenant_id == tid, Invoice.status.in_(["unpaid", "partial"]))
    ) or Decimal("0")

    low_stock = db.scalar(
        select(func.count())
        .select_from(StockLevel)
        .where(StockLevel.tenant_id == tid, StockLevel.quantity <= LOW_STOCK_THRESHOLD)
    ) or 0

    return ReportSummary(
        total_customers=count(Customer),
        total_products=count(Product),
        total_warehouses=count(Warehouse),
        total_distributors=count(Distributor),
        revenue_30d=Decimal(revenue_30d),
        outstanding=Decimal(outstanding),
        orders_30d=int(orders_30d),
        low_stock_count=int(low_stock),
    )


@router.get("/daily-revenue", response_model=list[DailyRevenuePoint])
def daily_revenue(tenant: CurrentTenant, db: DbSession, _: CurrentUser, days: int = 14):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    day = func.date_trunc("day", Order.created_at).label("day")
    rows = db.execute(
        select(day, func.sum(Order.total), func.count())
        .where(Order.tenant_id == tenant.id, Order.status != "cancelled", Order.created_at >= since)
        .group_by(day)
        .order_by(day)
    ).all()
    return [
        DailyRevenuePoint(date=r[0].date().isoformat(), revenue=Decimal(r[1] or 0), orders=int(r[2]))
        for r in rows
    ]
