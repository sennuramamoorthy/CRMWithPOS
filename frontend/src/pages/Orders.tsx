import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { api, Order } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

function statusTone(s: string): "default" | "success" | "warning" | "danger" | "info" {
  if (s === "confirmed") return "success";
  if (s === "cancelled") return "danger";
  return "default";
}

export function OrdersPage() {
  const [rows, setRows] = useState<Order[]>([]);

  async function load() {
    const { data } = await api.get<Order[]>("/orders");
    setRows(data);
  }
  useEffect(() => { load(); }, []);

  async function cancel(o: Order) {
    if (!confirm(`Cancel order ${o.code}?`)) return;
    await api.post(`/orders/${o.id}/cancel`);
    load();
  }

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-semibold">Orders</h1>
      <Card><CardContent>
        <DataTable
          rows={rows}
          columns={[
            { key: "code", header: "Order" },
            { key: "created_at", header: "Date", render: (r) => formatDate(r.created_at) },
            { key: "warehouse_id", header: "Warehouse #" },
            { key: "items", header: "Items", render: (r) => r.items.length },
            { key: "total", header: "Total", render: (r) => formatCurrency(r.total) },
            { key: "status", header: "Status", render: (r) => <Badge tone={statusTone(r.status)}>{r.status}</Badge> },
            {
              key: "__actions", header: "", className: "w-28 text-right",
              render: (r) => r.status === "confirmed"
                ? <Button size="sm" variant="outline" onClick={() => cancel(r)}>Cancel</Button>
                : null,
            },
          ]}
        />
      </CardContent></Card>
    </div>
  );
}
