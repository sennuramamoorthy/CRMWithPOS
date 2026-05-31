import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { Dialog } from "@/components/ui/Dialog";
import { Input, Label } from "@/components/ui/Input";
import { api, Invoice } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

function statusTone(s: string): "default" | "success" | "warning" | "danger" | "info" {
  if (s === "paid") return "success";
  if (s === "partial") return "warning";
  if (s === "void") return "danger";
  return "info";
}

export function InvoicesPage() {
  const [rows, setRows] = useState<Invoice[]>([]);
  const [paying, setPaying] = useState<Invoice | null>(null);
  const [form, setForm] = useState({ amount: "0", method: "cash", reference: "", note: "" });

  async function load() {
    const { data } = await api.get<Invoice[]>("/invoices");
    setRows(data);
  }
  useEffect(() => { load(); }, []);

  function openPay(inv: Invoice) {
    const due = Math.max(0, parseFloat(inv.total) - parseFloat(inv.amount_paid));
    setForm({ amount: due.toFixed(2), method: "cash", reference: "", note: "" });
    setPaying(inv);
  }

  async function submitPayment() {
    if (!paying) return;
    await api.post("/payments", {
      invoice_id: paying.id,
      amount: Number(form.amount),
      method: form.method,
      reference: form.reference || null,
      note: form.note || null,
    });
    setPaying(null);
    load();
  }

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-semibold">Invoices</h1>
      <Card><CardContent>
        <DataTable
          rows={rows}
          columns={[
            { key: "number", header: "Invoice" },
            { key: "issued_at", header: "Issued", render: (r) => formatDate(r.issued_at) },
            { key: "total", header: "Total", render: (r) => formatCurrency(r.total) },
            { key: "amount_paid", header: "Paid", render: (r) => formatCurrency(r.amount_paid) },
            {
              key: "due", header: "Due",
              render: (r) => formatCurrency(Math.max(0, parseFloat(r.total) - parseFloat(r.amount_paid))),
            },
            { key: "status", header: "Status", render: (r) => <Badge tone={statusTone(r.status)}>{r.status}</Badge> },
            {
              key: "__actions", header: "", className: "w-32 text-right",
              render: (r) => (r.status === "unpaid" || r.status === "partial")
                ? <Button size="sm" onClick={() => openPay(r)}>Record payment</Button>
                : null,
            },
          ]}
        />
      </CardContent></Card>

      <Dialog
        open={paying !== null} onClose={() => setPaying(null)}
        title={`Record payment · ${paying?.number ?? ""}`}
        footer={<>
          <Button variant="outline" onClick={() => setPaying(null)}>Cancel</Button>
          <Button onClick={submitPayment}>Save</Button>
        </>}
      >
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div><Label>Amount</Label><Input type="number" step="0.01" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} /></div>
            <div>
              <Label>Method</Label>
              <select
                className="h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm"
                value={form.method}
                onChange={(e) => setForm({ ...form, method: e.target.value })}
              >
                {["cash", "card", "bank", "upi", "other"].map((m) => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
          </div>
          <div><Label>Reference (optional)</Label><Input value={form.reference} onChange={(e) => setForm({ ...form, reference: e.target.value })} /></div>
          <div><Label>Note (optional)</Label><Input value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} /></div>
        </div>
      </Dialog>
    </div>
  );
}
