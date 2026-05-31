from decimal import Decimal

from fastapi import APIRouter, HTTPException, status

from ..core.crud import get_for_tenant, list_for_tenant
from ..dependencies import CurrentTenant, CurrentUser, DbSession
from ..models import Invoice, Payment
from ..schemas.common import PaymentCreate, PaymentOut

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("", response_model=list[PaymentOut])
def list_payments(tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return list_for_tenant(db, Payment, tenant.id)


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def record_payment(payload: PaymentCreate, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    if payload.amount <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "amount must be positive")

    invoice = get_for_tenant(db, Invoice, tenant.id, payload.invoice_id)
    if invoice.status == "void":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "cannot pay a void invoice")

    payment = Payment(
        tenant_id=tenant.id,
        invoice_id=invoice.id,
        amount=payload.amount,
        method=payload.method,
        reference=payload.reference,
        note=payload.note,
    )
    db.add(payment)

    invoice.amount_paid = (invoice.amount_paid or Decimal("0")) + payload.amount
    if invoice.amount_paid >= invoice.total:
        invoice.status = "paid"
    elif invoice.amount_paid > 0:
        invoice.status = "partial"

    db.commit()
    db.refresh(payment)
    return payment
