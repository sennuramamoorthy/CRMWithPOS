import { Link, NavLink, Outlet } from "react-router-dom";
import {
  Building2,
  Home,
  LogOut,
  Package,
  Receipt,
  Settings,
  ShoppingCart,
  Truck,
  Users,
  Warehouse,
  Wallet,
  BarChart3,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useTenant } from "@/contexts/TenantContext";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", label: "Dashboard", icon: Home },
  { to: "/pos", label: "POS", icon: ShoppingCart },
  { to: "/orders", label: "Orders", icon: Receipt },
  { to: "/invoices", label: "Invoices", icon: Receipt },
  { to: "/payments", label: "Payments", icon: Wallet },
  { to: "/customers", label: "Customers", icon: Users },
  { to: "/products", label: "Products", icon: Package },
  { to: "/warehouses", label: "Warehouses", icon: Warehouse },
  { to: "/distributors", label: "Distributors", icon: Truck },
  { to: "/reports", label: "Reports", icon: BarChart3 },
  { to: "/settings", label: "Settings", icon: Settings },
];

export function AppLayout() {
  const { user, logout } = useAuth();
  const { tenant, logoSrc } = useTenant();

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-64 shrink-0 border-r border-slate-200 bg-white flex flex-col">
        <Link to="/" className="flex items-center gap-3 px-5 py-4 border-b border-slate-100">
          {logoSrc ? (
            <img src={logoSrc} alt={tenant?.name ?? ""} className="h-9 w-9 rounded object-contain bg-slate-50" />
          ) : (
            <div className="h-9 w-9 rounded bg-brand text-brand-fg flex items-center justify-center font-bold">
              {(tenant?.name ?? "?").slice(0, 1)}
            </div>
          )}
          <div className="min-w-0">
            <div className="font-semibold text-sm truncate">{tenant?.name ?? "CRM"}</div>
            <div className="text-xs text-slate-500">{user?.full_name}</div>
          </div>
        </Link>

        <nav className="flex-1 overflow-y-auto py-2">
          {navItems.map((it) => (
            <NavLink
              key={it.to}
              to={it.to}
              end={it.to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 px-5 py-2 text-sm",
                  isActive
                    ? "bg-brand/10 text-brand font-medium border-l-2 border-brand"
                    : "text-slate-700 hover:bg-slate-50"
                )
              }
            >
              <it.icon size={16} />
              {it.label}
            </NavLink>
          ))}
        </nav>

        <button
          onClick={logout}
          className="flex items-center gap-3 px-5 py-3 text-sm text-slate-700 border-t border-slate-100 hover:bg-slate-50"
        >
          <LogOut size={16} />
          Sign out
        </button>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <header className="px-8 py-4 border-b border-slate-100 bg-white flex items-center gap-3">
          <Building2 size={18} className="text-slate-400" />
          <span className="text-sm text-slate-500">{tenant?.name ?? "—"}</span>
        </header>
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
