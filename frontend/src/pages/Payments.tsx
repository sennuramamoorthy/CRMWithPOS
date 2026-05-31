import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/Card";
import { DataTable } from "@/components/ui/DataTable";
import { api, Payment } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

export function PaymentsPage() {
  const [rows, setRows] = useState<Payment[]>([]);
  useEffect(() => { api.get<Payment[]>("/payments").then((r) => setRows(r.data)); }, []);
  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-semibold">Payments</h1>
      <Card><CardContent>
        <DataTable
          rows={rows}
          columns={[
            { key: "id", header: "#" },
            { key: "created_at", header: "Date", render: (r) => formatDate(r.created_at) },
            { key: "invoice_id", header: "Invoice #" },
            { key: "amount", header: "Amount", render: (r) => formatCurrency(r.amount) },
            { key: "method", header: "Method" },
            { key: "reference", header: "Reference" },
          ]}
        />
      </CardContent></Card>
    </div>
  );
}
