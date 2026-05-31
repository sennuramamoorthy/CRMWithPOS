"""Seed data for the CRM/POS demo.

Usage:
  python -m app.seeds                 # minimal seed (idempotent): 1 tenant, 1 admin,
                                      #   2 warehouses, 2 distributors, 3 products.
  python -m app.seeds --demo          # comprehensive demo:
                                      #   - 2 tenants (acme + globex)
                                      #   - 3 acme users (admin/manager/cashier)
                                      #   - 3 warehouses, 3 distributors, 6 products
                                      #   - 5 customers (individuals + companies)
                                      #   - 8 orders across the last 14 days
                                      #   - invoices in every status (paid/partial/unpaid/void)
                                      #   - payments via cash/card/upi/bank
                                      #   - low-stock items to trigger dashboard alerts
  python -m app.seeds --reset         # WIPE all tenants before seeding (DESTRUCTIVE).
                                      #   Combine with --demo to start fresh.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .core.security import hash_password
from .database import SessionLocal
from .models import (
    Customer,
    Distributor,
    Invoice,
    Order,
    OrderItem,
    Payment,
    Product,
    StockLevel,
    Tenant,
    User,
    Warehouse,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _wipe(db: Session) -> None:
    """Delete every business row. Order matters because of FK RESTRICT on
    `orders.warehouse_id` / `order_items.product_id`."""
    for model in (
        Payment, Invoice, OrderItem, Order, StockLevel,
        Product, Distributor, Warehouse, Customer, User, Tenant,
    ):
        db.execute(delete(model))
    db.commit()


# ---------------------------------------------------------------------------
# minimal seed (idempotent)
# ---------------------------------------------------------------------------

def seed_minimal() -> None:
    db = SessionLocal()
    try:
        tenant = db.scalar(select(Tenant).where(Tenant.slug == "acme"))
        if tenant is None:
            tenant = Tenant(slug="acme", name="Acme Trading Co.", primary_color="#2563eb")
            db.add(tenant)
            db.flush()

        if not db.scalar(select(User).where(User.email == "admin@acme.test")):
            db.add(User(
                tenant_id=tenant.id,
                email="admin@acme.test",
                full_name="Acme Admin",
                password_hash=hash_password("admin123"),
                role="admin",
            ))

        if not db.scalar(select(Warehouse).where(Warehouse.tenant_id == tenant.id).limit(1)):
            wh_main = Warehouse(tenant_id=tenant.id, name="Main Warehouse", code="WH-MAIN", city="Chennai")
            wh_north = Warehouse(tenant_id=tenant.id, name="North Hub", code="WH-NORTH", city="Bengaluru")
            db.add_all([wh_main, wh_north])
            db.flush()

            dist_a = Distributor(tenant_id=tenant.id, name="Coastal Distributors", code="D-COAST", region="South")
            dist_b = Distributor(tenant_id=tenant.id, name="Highland Supply", code="D-HIGH", region="North")
            db.add_all([dist_a, dist_b])
            db.flush()

            for sku, name, price, cost, did in (
                ("SKU-001", "Premium Tea 250g",   "249.00", "160.00", dist_a.id),
                ("SKU-002", "Filter Coffee 500g", "399.00", "260.00", dist_a.id),
                ("SKU-003", "Organic Honey 1kg",  "599.00", "380.00", dist_b.id),
            ):
                p = Product(tenant_id=tenant.id, sku=sku, name=name,
                            price=Decimal(price), cost=Decimal(cost), distributor_id=did)
                db.add(p)
                db.flush()
                db.add(StockLevel(tenant_id=tenant.id, warehouse_id=wh_main.id, product_id=p.id, quantity=50))
                db.add(StockLevel(tenant_id=tenant.id, warehouse_id=wh_north.id, product_id=p.id, quantity=20))

        db.commit()
        print("Seed (minimal) complete.")
        print("Login: admin@acme.test / admin123")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# comprehensive demo seed
# ---------------------------------------------------------------------------

def seed_demo() -> None:
    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)

        # --- Tenant 1: Acme Trading Co. ----------------------------------------
        acme = Tenant(slug="acme", name="Acme Trading Co.", primary_color="#2563eb")
        db.add(acme)
        db.flush()

        admin = User(
            tenant_id=acme.id, email="admin@acme.test", full_name="Acme Admin",
            password_hash=hash_password("admin123"), role="admin",
        )
        manager = User(
            tenant_id=acme.id, email="manager@acme.test", full_name="Aarav Krishnan",
            password_hash=hash_password("manager123"), role="manager",
        )
        cashier = User(
            tenant_id=acme.id, email="cashier@acme.test", full_name="Sneha Reddy",
            password_hash=hash_password("cashier123"), role="cashier",
        )
        db.add_all([admin, manager, cashier])
        db.flush()

        wh_main = Warehouse(
            tenant_id=acme.id, name="Main Warehouse", code="WH-MAIN", city="Chennai",
            address="14 Marina Drive", contact_name="Ravi Kumar", contact_phone="+91-44-1234-5678",
        )
        wh_north = Warehouse(
            tenant_id=acme.id, name="North Hub", code="WH-NORTH", city="Bengaluru",
            address="22 MG Road", contact_name="Lakshmi N", contact_phone="+91-80-9876-5432",
        )
        wh_west = Warehouse(
            tenant_id=acme.id, name="West Depot", code="WH-WEST", city="Mumbai",
            address="Plot 7, Andheri East", contact_name="Vikram Patel", contact_phone="+91-22-2345-6789",
        )
        db.add_all([wh_main, wh_north, wh_west])
        db.flush()

        dist_a = Distributor(
            tenant_id=acme.id, name="Coastal Distributors", code="D-COAST", region="South",
            contact_name="Ananya Pillai", contact_email="ops@coastal.example", contact_phone="+91-44-5555-1111",
        )
        dist_b = Distributor(
            tenant_id=acme.id, name="Highland Supply", code="D-HIGH", region="North",
            contact_name="Manish Singh", contact_email="orders@highland.example", contact_phone="+91-11-5555-2222",
        )
        dist_c = Distributor(
            tenant_id=acme.id, name="Spice Bazaar Imports", code="D-SPICE", region="West",
            contact_name="Faisal Khan", contact_email="trade@spicebazaar.example", contact_phone="+91-22-5555-3333",
        )
        db.add_all([dist_a, dist_b, dist_c])
        db.flush()

        products_spec = [
            ("SKU-001", "Premium Tea 250g",     "249.00", "160.00", dist_a.id),
            ("SKU-002", "Filter Coffee 500g",   "399.00", "260.00", dist_a.id),
            ("SKU-003", "Organic Honey 1kg",    "599.00", "380.00", dist_b.id),
            ("SKU-004", "Cardamom Pods 100g",   "459.00", "300.00", dist_c.id),
            ("SKU-005", "Coconut Oil 1L",       "329.00", "210.00", dist_a.id),
            ("SKU-006", "Specialty Saffron 1g", "899.00", "650.00", dist_c.id),
        ]
        products: dict[str, Product] = {}
        for sku, name, price, cost, did in products_spec:
            p = Product(tenant_id=acme.id, sku=sku, name=name,
                        price=Decimal(price), cost=Decimal(cost), distributor_id=did)
            db.add(p)
            products[sku] = p
        db.flush()

        tea      = products["SKU-001"]
        coffee   = products["SKU-002"]
        honey    = products["SKU-003"]
        cardamom = products["SKU-004"]
        coconut  = products["SKU-005"]
        saffron  = products["SKU-006"]

        # Stock — some warehouses deliberately under the low-stock threshold (≤5)
        stock_spec = [
            (tea,      [(wh_main, 60), (wh_north, 25), (wh_west, 15)]),
            (coffee,   [(wh_main, 30), (wh_north, 12), (wh_west, 8)]),
            (honey,    [(wh_main, 40), (wh_north, 18), (wh_west, 10)]),
            (cardamom, [(wh_main, 12), (wh_north, 4),  (wh_west, 6)]),   # north already low
            (coconut,  [(wh_main, 60), (wh_north, 25), (wh_west, 20)]),
            (saffron,  [(wh_main, 3),  (wh_north, 0),  (wh_west, 5)]),   # very low everywhere
        ]
        for p, levels in stock_spec:
            for wh, qty in levels:
                db.add(StockLevel(tenant_id=acme.id, warehouse_id=wh.id,
                                  product_id=p.id, quantity=qty))
        db.flush()

        customers_spec = [
            ("Aarav Sharma",     "aarav@example.com",            "+91-98000-11111", None,                "12 Elm Street, Chennai",  "Walk-in regular"),
            ("Priya Iyer",       "priya@iyergroup.example",      "+91-98000-22222", "Iyer Group",        "Office 401, Anna Salai",  "Bulk buyer"),
            ("Quantum Foods Ltd","procurement@quantum.example",  "+91-22-4444-3333","Quantum Foods Ltd", "Andheri West, Mumbai",    "Net-30 terms"),
            ("NaturalsGroup",    "buying@naturalsgroup.example", "+91-80-2222-5555","NaturalsGroup",     "MG Road, Bengaluru",      "Premium client"),
            ("Rohan Mehta",      "rohan.m@example.com",          "+91-98000-33333", None,                "JP Nagar, Bengaluru",     None),
        ]
        customers: dict[str, Customer] = {}
        for name, email, phone, company, addr, notes in customers_spec:
            c = Customer(tenant_id=acme.id, name=name, email=email, phone=phone,
                         company=company, address=addr, notes=notes)
            db.add(c)
            customers[name] = c
        db.flush()

        # --- Orders ----------------------------------------------------------------
        # Each order: days_ago (offset from now), customer-or-None, warehouse,
        # line items, tax/discount, and final invoice status.
        # status options: "paid" | "partial" | "unpaid" | "cancelled"

        def make_order(
            *,
            days_ago: float,
            customer: Customer | None,
            warehouse: Warehouse,
            lines: list[tuple[Product, int]],
            tax: Decimal = Decimal("0"),
            discount: Decimal = Decimal("0"),
            status: str = "paid",
            partial_amount: Decimal | None = None,
            method: str = "cash",
        ) -> None:
            created = now - timedelta(days=days_ago)
            subtotal = Decimal("0")
            order_items: list[OrderItem] = []
            for product, qty in lines:
                line_total = product.price * qty
                subtotal += line_total
                level = db.scalar(select(StockLevel).where(
                    StockLevel.tenant_id == acme.id,
                    StockLevel.warehouse_id == warehouse.id,
                    StockLevel.product_id == product.id,
                ))
                assert level is not None and level.quantity >= qty, (
                    f"seed bug: not enough {product.sku} in {warehouse.code} "
                    f"(have {None if level is None else level.quantity}, need {qty})"
                )
                level.quantity -= qty
                order_items.append(OrderItem(
                    tenant_id=acme.id, product_id=product.id, quantity=qty,
                    unit_price=product.price, line_total=line_total,
                ))

            total = subtotal + tax - discount
            order = Order(
                tenant_id=acme.id, code="PENDING",
                customer_id=customer.id if customer else None,
                warehouse_id=warehouse.id, status="confirmed",
                subtotal=subtotal, tax=tax, discount=discount, total=total,
                created_by=admin.id, created_at=created, items=order_items,
            )
            db.add(order)
            db.flush()
            order.code = f"ORD-{created.strftime('%y%m%d')}-{order.id:05d}"

            invoice = Invoice(
                tenant_id=acme.id,
                number=f"INV-{created.strftime('%y%m%d')}-{order.id:05d}",
                order_id=order.id,
                customer_id=customer.id if customer else None,
                total=total, amount_paid=Decimal("0"),
                status="unpaid" if total > 0 else "paid",
                issued_at=created,
            )
            db.add(invoice)
            db.flush()

            if status == "cancelled":
                for item in order.items:
                    level = db.scalar(select(StockLevel).where(
                        StockLevel.tenant_id == acme.id,
                        StockLevel.warehouse_id == order.warehouse_id,
                        StockLevel.product_id == item.product_id,
                    ))
                    level.quantity += item.quantity
                order.status = "cancelled"
                invoice.status = "void"
                return

            if status == "paid":
                amt = total
            elif status == "partial":
                assert partial_amount is not None, "partial requires partial_amount"
                amt = Decimal(partial_amount)
            else:  # "unpaid"
                amt = Decimal("0")

            if amt > 0:
                db.add(Payment(
                    tenant_id=acme.id, invoice_id=invoice.id, amount=amt,
                    method=method, reference=f"{method.upper()}-{invoice.number[-5:]}",
                    created_at=created + timedelta(hours=2),
                ))
                invoice.amount_paid = amt
                invoice.status = "paid" if amt >= total else "partial"

        # Eight orders across ~14 days — covers every invoice status + every payment method.
        make_order(days_ago=13, customer=None,                       warehouse=wh_main,
                   lines=[(tea, 2), (coffee, 1)],
                   status="paid", method="cash")

        make_order(days_ago=11, customer=customers["Aarav Sharma"],  warehouse=wh_main,
                   lines=[(honey, 3), (cardamom, 1)],
                   status="paid", method="upi")

        make_order(days_ago=9,  customer=customers["Priya Iyer"],    warehouse=wh_north,
                   lines=[(coffee, 4), (tea, 2)], tax=Decimal("100.00"),
                   status="partial", partial_amount=Decimal("1000.00"), method="bank")

        make_order(days_ago=7,  customer=customers["Quantum Foods Ltd"], warehouse=wh_west,
                   lines=[(honey, 10), (coconut, 8), (saffron, 1)], tax=Decimal("400.00"),
                   status="unpaid")  # large outstanding invoice

        make_order(days_ago=5,  customer=None,                       warehouse=wh_main,
                   lines=[(coconut, 2), (tea, 1)],
                   status="paid", method="card")

        make_order(days_ago=4,  customer=customers["Aarav Sharma"],  warehouse=wh_north,
                   lines=[(tea, 2), (cardamom, 1)],
                   status="cancelled")  # void invoice + stock returned

        make_order(days_ago=2,  customer=customers["NaturalsGroup"], warehouse=wh_north,
                   lines=[(tea, 5), (coffee, 3), (honey, 2), (coconut, 4), (cardamom, 2)],
                   discount=Decimal("200.00"),
                   status="paid", method="cash")

        make_order(days_ago=0,  customer=customers["Rohan Mehta"],   warehouse=wh_main,
                   lines=[(coffee, 1), (honey, 1)],
                   status="paid", method="card")

        db.commit()

        # --- Tenant 2: Globex (multi-tenancy demo) ---------------------------------
        globex = Tenant(slug="globex", name="Globex Corporation", primary_color="#10b981")
        db.add(globex)
        db.flush()
        db.add(User(
            tenant_id=globex.id, email="admin@globex.test", full_name="Globex Admin",
            password_hash=hash_password("globex123"), role="admin",
        ))
        gx_wh = Warehouse(tenant_id=globex.id, name="HQ Storage", code="GX-HQ", city="Hyderabad")
        db.add(gx_wh)
        gx_dist = Distributor(tenant_id=globex.id, name="Acme Logistics", code="GX-LOG", region="South")
        db.add(gx_dist)
        db.flush()
        gx_p = Product(
            tenant_id=globex.id, sku="GX-001", name="Test Widget",
            price=Decimal("99.00"), cost=Decimal("50.00"), distributor_id=gx_dist.id,
        )
        db.add(gx_p)
        db.flush()
        db.add(StockLevel(tenant_id=globex.id, warehouse_id=gx_wh.id,
                          product_id=gx_p.id, quantity=200))
        db.commit()

        print("Demo seed complete.\n")
        print("Tenant 1 — Acme Trading Co. (slug=acme, brand #2563eb)")
        print("  admin@acme.test   / admin123    (admin)")
        print("  manager@acme.test / manager123  (manager)")
        print("  cashier@acme.test / cashier123  (cashier)\n")
        print("Tenant 2 — Globex Corporation (slug=globex, brand #10b981)")
        print("  admin@globex.test / globex123   (admin)\n")
        print("Acme data:")
        print("  3 warehouses · 3 distributors · 6 products · 5 customers")
        print("  8 orders across the last 14 days")
        print("  invoices in every status:  paid · partial · unpaid · void")
        print("  payments via:              cash · card · upi · bank")
        print("  low-stock items (qty ≤ 5): saffron (everywhere), cardamom (north),")
        print("                             coffee (north), honey (west)")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed CRM/POS data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--demo", action="store_true",
                        help="Seed comprehensive demo data (2 tenants, 3 users, 8 orders, …).")
    parser.add_argument("--reset", action="store_true",
                        help="WIPE all tenants before seeding. DESTRUCTIVE.")
    args = parser.parse_args()

    if args.reset:
        db = SessionLocal()
        try:
            _wipe(db)
            print("Wiped existing tenants.")
        finally:
            db.close()

    if args.demo:
        db = SessionLocal()
        try:
            if db.scalar(select(Tenant).where(Tenant.slug == "acme")) is not None:
                print(
                    "acme tenant already exists. Run `python -m app.seeds --demo --reset` "
                    "(or `make seed-fresh`) to wipe and reseed.",
                    file=sys.stderr,
                )
                sys.exit(1)
        finally:
            db.close()
        seed_demo()
    else:
        seed_minimal()


if __name__ == "__main__":
    main()
