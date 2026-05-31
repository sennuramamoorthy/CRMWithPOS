import { createContext, ReactNode, useCallback, useContext, useEffect, useState } from "react";
import { api, API_URL, Tenant } from "@/lib/api";
import { useAuth } from "./AuthContext";

interface TenantCtx {
  tenant: Tenant | null;
  refresh: () => Promise<void>;
  logoSrc: string | null;
}

const Ctx = createContext<TenantCtx | null>(null);

export function TenantProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [tenant, setTenant] = useState<Tenant | null>(null);

  const refresh = useCallback(async () => {
    if (!user) {
      setTenant(null);
      return;
    }
    const { data } = await api.get<Tenant>("/tenant");
    setTenant(data);
  }, [user]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (tenant?.primary_color) {
      document.documentElement.style.setProperty("--color-brand", tenant.primary_color);
    }
    if (tenant?.name) document.title = tenant.name;
  }, [tenant]);

  const logoSrc = tenant?.logo_url ? `${API_URL}${tenant.logo_url}` : null;

  return <Ctx.Provider value={{ tenant, refresh, logoSrc }}>{children}</Ctx.Provider>;
}

export function useTenant() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useTenant outside TenantProvider");
  return v;
}
