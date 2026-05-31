import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { api, DailyRevenuePoint, Summary } from "@/lib/api";
import { formatCurrency } from "@/lib/utils";

export function ReportsPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [daily, setDaily] = useState<DailyRevenuePoint[]>([]);

  useEffect(() => {
    api.get<Summary>("/reports/summary").then((r) => setSummary(r.data));
    api.get<DailyRevenuePoint[]>("/reports/daily-revenue?days=30").then((r) => setDaily(r.data));
  }, []);

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-semibold">Reports</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card><CardContent>
          <div className="text-xs uppercase text-slate-500">Revenue 30d</div>
          <div className="mt-1 text-2xl font-semibold">{formatCurrency(summary?.revenue_30d ?? 0)}</div>
        </CardContent></Card>
        <Card><CardContent>
          <div className="text-xs uppercase text-slate-500">Orders 30d</div>
          <div className="mt-1 text-2xl font-semibold">{summary?.orders_30d ?? "—"}</div>
        </CardContent></Card>
        <Card><CardContent>
          <div className="text-xs uppercase text-slate-500">Outstanding</div>
          <div className="mt-1 text-2xl font-semibold">{formatCurrency(summary?.outstanding ?? 0)}</div>
        </CardContent></Card>
        <Card><CardContent>
          <div className="text-xs uppercase text-slate-500">Low stock items</div>
          <div className="mt-1 text-2xl font-semibold">{summary?.low_stock_count ?? "—"}</div>
        </CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Daily revenue (last 30 days)</CardTitle></CardHeader>
        <CardContent>
          {daily.length === 0 ? (
            <div className="text-sm text-slate-500">No data yet.</div>
          ) : (
            <table className="min-w-full text-sm">
              <thead className="text-slate-500"><tr>
                <th className="text-left py-2">Date</th>
                <th className="text-right py-2">Orders</th>
                <th className="text-right py-2">Revenue</th>
              </tr></thead>
              <tbody className="divide-y divide-slate-100">
                {daily.map((d) => (
                  <tr key={d.date}>
                    <td className="py-2">{d.date}</td>
                    <td className="text-right">{d.orders}</td>
                    <td className="text-right">{formatCurrency(d.revenue)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
