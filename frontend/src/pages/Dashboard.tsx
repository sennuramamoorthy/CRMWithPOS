import { useEffect, useState } from "react";
import { api, DailyRevenuePoint, Summary } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/Card";
import { formatCurrency } from "@/lib/utils";

export function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [daily, setDaily] = useState<DailyRevenuePoint[]>([]);

  useEffect(() => {
    api.get<Summary>("/reports/summary").then((r) => setSummary(r.data));
    api.get<DailyRevenuePoint[]>("/reports/daily-revenue").then((r) => setDaily(r.data));
  }, []);

  const tiles = [
    { label: "Revenue (30d)", value: formatCurrency(summary?.revenue_30d ?? 0) },
    { label: "Orders (30d)", value: summary?.orders_30d ?? "—" },
    { label: "Outstanding", value: formatCurrency(summary?.outstanding ?? 0) },
    { label: "Low stock items", value: summary?.low_stock_count ?? "—" },
    { label: "Customers", value: summary?.total_customers ?? "—" },
    { label: "Products", value: summary?.total_products ?? "—" },
    { label: "Warehouses", value: summary?.total_warehouses ?? "—" },
    { label: "Distributors", value: summary?.total_distributors ?? "—" },
  ];

  const maxRev = Math.max(1, ...daily.map((d) => parseFloat(d.revenue)));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {tiles.map((t) => (
          <Card key={t.label}>
            <CardContent>
              <div className="text-xs uppercase tracking-wide text-slate-500">{t.label}</div>
              <div className="mt-2 text-2xl font-semibold">{t.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card>
        <CardContent>
          <div className="mb-3 font-medium">Daily revenue</div>
          {daily.length === 0 ? (
            <div className="text-sm text-slate-500">No orders yet.</div>
          ) : (
            <div className="flex items-end gap-2 h-40">
              {daily.map((d) => {
                const h = Math.max(4, Math.round((parseFloat(d.revenue) / maxRev) * 140));
                return (
                  <div key={d.date} className="flex-1 flex flex-col items-center gap-1" title={`${d.date}: ${d.revenue}`}>
                    <div className="w-full rounded-t bg-brand/80" style={{ height: h }} />
                    <div className="text-[10px] text-slate-500">{d.date.slice(5)}</div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
