from fastapi import APIRouter

from ..core.crud import get_for_tenant, list_for_tenant
from ..dependencies import CurrentTenant, CurrentUser, DbSession
from ..models import Invoice
from ..schemas.common import InvoiceOut

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("", response_model=list[InvoiceOut])
def list_invoices(tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return list_for_tenant(db, Invoice, tenant.id)


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, tenant: CurrentTenant, db: DbSession, _: CurrentUser):
    return get_for_tenant(db, Invoice, tenant.id, invoice_id)
