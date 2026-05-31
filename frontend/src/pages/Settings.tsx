import { ChangeEvent, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Input, Label } from "@/components/ui/Input";
import { api } from "@/lib/api";
import { useTenant } from "@/contexts/TenantContext";

export function SettingsPage() {
  const { tenant, refresh, logoSrc } = useTenant();
  const [name, setName] = useState(tenant?.name ?? "");
  const [color, setColor] = useState(tenant?.primary_color ?? "#2563eb");
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingLogo, setSavingLogo] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function saveProfile() {
    setSavingProfile(true);
    setMsg(null);
    try {
      await api.patch("/tenant", { name, primary_color: color });
      await refresh();
      setMsg("Saved.");
    } catch (e: any) {
      setMsg(e?.response?.data?.detail ?? "Save failed");
    } finally {
      setSavingProfile(false);
    }
  }

  async function uploadLogo(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setSavingLogo(true);
    setMsg(null);
    const fd = new FormData();
    fd.append("file", file);
    try {
      await api.post("/tenant/logo", fd, { headers: { "Content-Type": "multipart/form-data" } });
      await refresh();
      setMsg("Logo updated.");
    } catch (err: any) {
      setMsg(err?.response?.data?.detail ?? "Upload failed");
    } finally {
      setSavingLogo(false);
      e.target.value = "";
    }
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <h1 className="text-2xl font-semibold">Application settings</h1>

      <Card>
        <CardHeader><CardTitle>Branding</CardTitle></CardHeader>
        <CardContent className="space-y-5">
          <div className="flex items-center gap-5">
            <div className="h-20 w-20 rounded border border-slate-200 bg-slate-50 flex items-center justify-center overflow-hidden">
              {logoSrc ? (
                <img src={logoSrc} alt="" className="h-full w-full object-contain" />
              ) : (
                <span className="text-slate-400 text-xs">No logo</span>
              )}
            </div>
            <div>
              <label className="inline-block">
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/svg+xml,image/webp"
                  className="hidden"
                  onChange={uploadLogo}
                />
                <span className="inline-flex items-center justify-center gap-2 rounded-md font-medium transition h-10 px-4 text-sm border border-slate-300 text-slate-700 hover:bg-slate-50 cursor-pointer">
                  {savingLogo ? "Uploading…" : "Upload new logo"}
                </span>
              </label>
              <p className="text-xs text-slate-500 mt-2">PNG, JPG, SVG, or WebP. Shown across the application.</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Application name</Label>
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Acme Trading Co." />
              <p className="text-xs text-slate-500 mt-1">Displayed in the sidebar, header, and browser tab.</p>
            </div>
            <div>
              <Label>Brand color</Label>
              <div className="flex items-center gap-3">
                <input
                  type="color"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  className="h-10 w-14 rounded border border-slate-300"
                />
                <Input value={color} onChange={(e) => setColor(e.target.value)} className="flex-1" />
              </div>
            </div>
          </div>

          {msg && <div className="text-sm text-slate-600">{msg}</div>}

          <div className="flex justify-end">
            <Button onClick={saveProfile} disabled={savingProfile}>
              {savingProfile ? "Saving…" : "Save changes"}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
