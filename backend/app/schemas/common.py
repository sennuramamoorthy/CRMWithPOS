from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- auth ----------

class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- tenant ----------

class TenantOut(ORMModel):
    id: int
    slug: str
    name: str
    logo_url: Optional[str] = None
    primary_color: str


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    primary_color: Optional[str] = None


# ---------- user ----------

class UserOut(ORMModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "cashier"


# ---------- warehouse ----------

class WarehouseBase(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    city: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


class WarehouseOut(ORMModel, WarehouseBase):
    id: int
    created_at: datetime


# ---------- distributor ----------

class DistributorBase(BaseModel):
    name: str
    code: str
    region: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None


class DistributorCreate(DistributorBase):
    pass


class DistributorUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    region: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None


class DistributorOut(ORMModel):
    id: int
    name: str
    code: str
    region: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime


# ---------- product / stock ----------

class ProductBase(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    unit: str = "pcs"
    price: Decimal = Decimal("0")
    cost: Decimal = Decimal("0")
    distributor_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    distributor_id: Optional[int] = None


class ProductOut(ORMModel, ProductBase):
    id: int
    created_at: datetime


class StockLevelOut(ORMModel):
    id: int
    warehouse_id: int
    product_id: int
    quantity: int


class StockAdjust(BaseModel):
    warehouse_id: int
    product_id: int
    delta: int  # positive to add, negative to remove


# ---------- customer ----------

class CustomerBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class CustomerOut(ORMModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


# ---------- orders ----------

class OrderItemIn(BaseModel):
    product_id: int
    quantity: int
    unit_price: Optional[Decimal] = None  # falls back to product.price


class OrderItemOut(ORMModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderCreate(BaseModel):
    customer_id: Optional[int] = None
    warehouse_id: int
    items: list[OrderItemIn]
    tax: Decimal = Decimal("0")
    discount: Decimal = Decimal("0")


class OrderOut(ORMModel):
    id: int
    code: str
    customer_id: Optional[int]
    warehouse_id: int
    status: str
    subtotal: Decimal
    tax: Decimal
    discount: Decimal
    total: Decimal
    created_at: datetime
    items: list[OrderItemOut] = []


# ---------- invoices / payments ----------

class InvoiceOut(ORMModel):
    id: int
    number: str
    order_id: int
    customer_id: Optional[int]
    total: Decimal
    amount_paid: Decimal
    status: str
    issued_at: datetime
    due_at: Optional[datetime] = None


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: Decimal
    method: str = "cash"
    reference: Optional[str] = None
    note: Optional[str] = None


class PaymentOut(ORMModel):
    id: int
    invoice_id: int
    amount: Decimal
    method: str
    reference: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime


# ---------- reports ----------

class ReportSummary(BaseModel):
    total_customers: int
    total_products: int
    total_warehouses: int
    total_distributors: int
    revenue_30d: Decimal
    outstanding: Decimal
    orders_30d: int
    low_stock_count: int


class DailyRevenuePoint(BaseModel):
    date: str
    revenue: Decimal
    orders: int
