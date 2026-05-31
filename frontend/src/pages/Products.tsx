import { useEffect, useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { Dialog } from "@/components/ui/Dialog";
import { Input, Label } from "@/components/ui/Input";
import { api, Distributor, Product, StockLevel, Warehouse } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

type ProductForm = {
  sku: string;
  name: string;
  unit: string;
  price: string;
  cost: string;
  distributor_id: number | null;
  description?: string;
};

const blank: ProductForm = { sku: "", name: "", unit: "pcs", price: "0", cost: "0", distributor_id: null };

export function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [distributors, setDistributors] = useState<Distributor[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [stock, setStock] = useState<StockLevel[]>([]);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Product | null>(null);
  const [form, setForm] = useState<ProductForm>(blank);

  const [adjustOpen, setAdjustOpen] = useState(false);
  const [adjustForm, setAdjustForm] = useState<{ product_id: number | null; warehouse_id: number | null; delta: number }>({
    product_id: null, warehouse_id: null, delta: 0,
  });

  async function loadAll() {
    const [p, d, w, s] = await Promise.all([
      api.get<Product[]>("/products"),
      api.get<Distributor[]>("/distributors"),
      api.get<Warehouse[]>("/warehouses"),
      api.get<StockLevel[]>("/products/stock/levels"),
    ]);
    setProducts(p.data); setDistributors(d.data); setWarehouses(w.data); setStock(s.data);
  }
  useEffect(() => { loadAll(); }, []);

  function distName(id: number | null | undefined) {
    return distributors.find((d) => d.id === id)?.name ?? "—";
  }

  function stockFor(productId: number) {
    return stock.filter((s) => s.product_id === productId);
  }

  function whName(id: number) {
    return warehouses.find((w) => w.id === id)?.name ?? `#${id}`;
  }

  function openCreate() {
    setEditing(null);
    setForm(blank);
    setOpen(true);
  }

  function openEdit(p: Product) {
    setEditing(p);
    setForm({
      sku: p.sku, name: p.name, unit: p.unit,
      price: String(p.price), cost: String(p.cost),
      distributor_id: p.distributor_id ?? null,
      description: p.description ?? "",
    });
    setOpen(true);
  }

  async function save() {
    const payload = { ...form, price: Number(form.price), cost: Number(form.cost) };
    if (editing) await api.patch(`/products/${editing.id}`, payload);
    else await api.post("/products", payload);
    setOpen(false);
    await loadAll();
  }

  async function remove(p: Product) {
    if (!confirm("Delete this product?")) return;
    await api.delete(`/products/${p.id}`);
    await loadAll();
  }

  async function adjustStock() {
    if (!adjustForm.product_id || !adjustForm.warehouse_id) return;
    await api.post("/products/stock/adjust", adjustForm);
    setAdjustOpen(false);
    await loadAll();
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Products</h1>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => { setAdjustForm({ product_id: null, warehouse_id: null, delta: 0 }); setAdjustOpen(true); }}>
            Adjust stock
          </Button>
          <Button onClick={openCreate}><Plus size={16} /> New</Button>
        </div>
      </div>

      <Card>
        <CardContent>
          <DataTable
            rows={products}
            columns={[
              { key: "sku", header: "SKU" },
              { key: "name", header: "Name" },
              { key: "price", header: "Price", render: (p) => formatCurrency(p.price) },
              { key: "distributor", header: "Distributor", render: (p) => distName(p.distributor_id) },
              {
                key: "stock", header: "Stock by warehouse",
                render: (p) => {
                  const levels = stockFor(p.id);
                  if (levels.length === 0) return <span className="text-slate-400">none</span>;
                  return (
                    <div className="flex flex-wrap gap-2">
                      {levels.map((l) => (
                        <span key={l.id} className="rounded bg-slate-100 px-2 py-0.5 text-xs">
                          {whName(l.warehouse_id)}: <b>{l.quantity}</b>
                        </span>
                      ))}
                    </div>
                  );
                },
              },
              {
                key: "__actions", header: "", className: "w-28 text-right",
                render: (p) => (
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="sm" onClick={() => openEdit(p)}><Pencil size={14} /></Button>
                    <Button variant="ghost" size="sm" onClick={() => remove(p)}><Trash2 size={14} className="text-rose-600" /></Button>
                  </div>
                ),
              },
            ]}
          />
        </CardContent>
      </Card>

      <Dialog
        open={open} onClose={() => setOpen(false)}
        title={editing ? "Edit product" : "New product"}
        footer={<>
          <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={save}>Save</Button>
        </>}
      >
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div><Label>SKU</Label><Input value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} /></div>
            <div><Label>Unit</Label><Input value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} /></div>
          </div>
          <div><Label>Name</Label><Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Price</Label><Input type="number" step="0.01" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} /></div>
            <div><Label>Cost</Label><Input type="number" step="0.01" value={form.cost} onChange={(e) => setForm({ ...form, cost: e.target.value })} /></div>
          </div>
          <div>
            <Label>Distributor</Label>
            <select
              className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm"
              value={form.distributor_id ?? ""}
              onChange={(e) => setForm({ ...form, distributor_id: e.target.value ? Number(e.target.value) : null })}
            >
              <option value="">— none —</option>
              {distributors.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
        </div>
      </Dialog>

      <Dialog
        open={adjustOpen} onClose={() => setAdjustOpen(false)}
        title="Adjust stock"
        footer={<>
          <Button variant="outline" onClick={() => setAdjustOpen(false)}>Cancel</Button>
          <Button onClick={adjustStock}>Apply</Button>
        </>}
      >
        <div className="space-y-3">
          <div>
            <Label>Product</Label>
            <select
              className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm"
              value={adjustForm.product_id ?? ""}
              onChange={(e) => setAdjustForm({ ...adjustForm, product_id: Number(e.target.value) })}
            >
              <option value="">— select —</option>
              {products.map((p) => <option key={p.id} value={p.id}>{p.sku} — {p.name}</option>)}
            </select>
          </div>
          <div>
            <Label>Warehouse</Label>
            <select
              className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm"
              value={adjustForm.warehouse_id ?? ""}
              onChange={(e) => setAdjustForm({ ...adjustForm, warehouse_id: Number(e.target.value) })}
            >
              <option value="">— select —</option>
              {warehouses.map((w) => <option key={w.id} value={w.id}>{w.name}</option>)}
            </select>
          </div>
          <div>
            <Label>Delta (positive to add, negative to remove)</Label>
            <Input type="number" value={adjustForm.delta} onChange={(e) => setAdjustForm({ ...adjustForm, delta: Number(e.target.value) })} />
          </div>
        </div>
      </Dialog>
    </div>
  );
}
