import { useEffect, useMemo, useState } from "react";
import { Minus, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input, Label } from "@/components/ui/Input";
import { api, Customer, Product, StockLevel, Warehouse } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

type CartLine = { product_id: number; name: string; sku: string; price: number; quantity: number };

export function POSPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [stock, setStock] = useState<StockLevel[]>([]);
  const [search, setSearch] = useState("");
  const [warehouseId, setWarehouseId] = useState<number | null>(null);
  const [customerId, setCustomerId] = useState<number | null>(null);
  const [tax, setTax] = useState(0);
  const [discount, setDiscount] = useState(0);
  const [cart, setCart] = useState<CartLine[]>([]);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function loadAll() {
    const [p, w, c, s] = await Promise.all([
      api.get<Product[]>("/products"),
      api.get<Warehouse[]>("/warehouses"),
      api.get<Customer[]>("/customers"),
      api.get<StockLevel[]>("/products/stock/levels"),
    ]);
    setProducts(p.data); setWarehouses(w.data); setCustomers(c.data); setStock(s.data);
    if (!warehouseId && w.data.length) setWarehouseId(w.data[0].id);
  }
  useEffect(() => { loadAll(); }, []);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    if (!q) return products;
    return products.filter((p) => p.name.toLowerCase().includes(q) || p.sku.toLowerCase().includes(q));
  }, [products, search]);

  function stockFor(productId: number) {
    if (!warehouseId) return 0;
    return stock.find((s) => s.product_id === productId && s.warehouse_id === warehouseId)?.quantity ?? 0;
  }

  function addToCart(p: Product) {
    const existing = cart.find((c) => c.product_id === p.id);
    if (existing) {
      setCart(cart.map((c) => c.product_id === p.id ? { ...c, quantity: c.quantity + 1 } : c));
    } else {
      setCart([...cart, { product_id: p.id, name: p.name, sku: p.sku, price: parseFloat(p.price), quantity: 1 }]);
    }
  }
  function setQty(productId: number, qty: number) {
    if (qty <= 0) return setCart(cart.filter((c) => c.product_id !== productId));
    setCart(cart.map((c) => c.product_id === productId ? { ...c, quantity: qty } : c));
  }

  const subtotal = cart.reduce((acc, c) => acc + c.price * c.quantity, 0);
  const total = subtotal + tax - discount;

  async function checkout() {
    if (!warehouseId || cart.length === 0) return;
    setBusy(true); setMsg(null);
    try {
      const { data } = await api.post("/orders", {
        customer_id: customerId,
        warehouse_id: warehouseId,
        items: cart.map((c) => ({ product_id: c.product_id, quantity: c.quantity, unit_price: c.price })),
        tax, discount,
      });
      setMsg(`Order ${data.code} created · total ${formatCurrency(data.total)}`);
      setCart([]); setTax(0); setDiscount(0);
      await loadAll();
    } catch (e: any) {
      setMsg(e?.response?.data?.detail ?? "Checkout failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <div className="lg:col-span-2 space-y-4">
        <div className="flex items-center justify-between gap-3">
          <h1 className="text-2xl font-semibold">Point of Sale</h1>
          <select
            className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
            value={warehouseId ?? ""}
            onChange={(e) => setWarehouseId(Number(e.target.value))}
          >
            {warehouses.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
          </select>
        </div>
        <Input placeholder="Search products by name or SKU…" value={search} onChange={(e) => setSearch(e.target.value)} />
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {filtered.map((p) => {
            const stk = stockFor(p.id);
            return (
              <button
                key={p.id}
                onClick={() => addToCart(p)}
                disabled={stk <= 0}
                className="text-left rounded-lg border border-slate-200 bg-white p-3 hover:border-brand disabled:opacity-50 disabled:hover:border-slate-200"
              >
                <div className="text-xs text-slate-500">{p.sku}</div>
                <div className="font-medium text-sm truncate">{p.name}</div>
                <div className="mt-1 flex items-center justify-between text-sm">
                  <span>{formatCurrency(p.price)}</span>
                  <span className={stk <= 5 ? "text-rose-600" : "text-slate-500"}>stock {stk}</span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <Card className="self-start sticky top-4">
        <CardHeader><CardTitle>Cart</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div>
            <Label>Customer (optional)</Label>
            <select
              className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm"
              value={customerId ?? ""}
              onChange={(e) => setCustomerId(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">Walk-in</option>
              {customers.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {cart.length === 0 && <div className="text-sm text-slate-400">Cart is empty.</div>}
            {cart.map((c) => (
              <div key={c.product_id} className="flex items-center gap-2 text-sm">
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{c.name}</div>
                  <div className="text-xs text-slate-500">{formatCurrency(c.price)}</div>
                </div>
                <div className="flex items-center gap-1">
                  <Button size="sm" variant="outline" onClick={() => setQty(c.product_id, c.quantity - 1)}><Minus size={12} /></Button>
                  <span className="w-7 text-center">{c.quantity}</span>
                  <Button size="sm" variant="outline" onClick={() => setQty(c.product_id, c.quantity + 1)}><Plus size={12} /></Button>
                  <Button size="sm" variant="ghost" onClick={() => setQty(c.product_id, 0)}><Trash2 size={12} /></Button>
                </div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Tax</Label><Input type="number" value={tax} onChange={(e) => setTax(Number(e.target.value))} /></div>
            <div><Label>Discount</Label><Input type="number" value={discount} onChange={(e) => setDiscount(Number(e.target.value))} /></div>
          </div>
          <div className="border-t border-slate-100 pt-3 space-y-1 text-sm">
            <div className="flex justify-between"><span>Subtotal</span><span>{formatCurrency(subtotal)}</span></div>
            <div className="flex justify-between"><span>Tax</span><span>{formatCurrency(tax)}</span></div>
            <div className="flex justify-between"><span>Discount</span><span>− {formatCurrency(discount)}</span></div>
            <div className="flex justify-between text-base font-semibold pt-1 border-t border-slate-100"><span>Total</span><span>{formatCurrency(total)}</span></div>
          </div>
          <Button onClick={checkout} disabled={busy || cart.length === 0} className="w-full">
            {busy ? "Processing…" : "Checkout"}
          </Button>
          {msg && <div className="text-sm text-slate-600">{msg}</div>}
        </CardContent>
      </Card>
    </div>
  );
}
