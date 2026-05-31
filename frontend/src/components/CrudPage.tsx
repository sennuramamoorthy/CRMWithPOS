import { ReactNode, useEffect, useState } from "react";
import { Plus, Pencil, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Card, CardContent } from "@/components/ui/Card";
import { Column, DataTable } from "@/components/ui/DataTable";
import { Dialog } from "@/components/ui/Dialog";
import { api } from "@/lib/api";

export type Field<T> = {
  name: keyof T & string;
  label: string;
  type?: "text" | "number" | "textarea";
  required?: boolean;
  step?: string;
};

export function CrudPage<T extends { id: number }>({
  title,
  endpoint,
  fields,
  columns,
  emptyDefaults,
}: {
  title: string;
  endpoint: string;
  fields: Field<T>[];
  columns: Column<T>[];
  emptyDefaults: Partial<T>;
}) {
  const [rows, setRows] = useState<T[]>([]);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<T | null>(null);
  const [form, setForm] = useState<Partial<T>>({});
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function load() {
    const { data } = await api.get<T[]>(endpoint);
    setRows(data);
  }
  useEffect(() => { load(); }, [endpoint]);

  function openCreate() {
    setEditing(null);
    setForm({ ...emptyDefaults });
    setErr(null);
    setOpen(true);
  }

  function openEdit(row: T) {
    setEditing(row);
    setForm({ ...row });
    setErr(null);
    setOpen(true);
  }

  async function save() {
    setBusy(true);
    setErr(null);
    try {
      if (editing) {
        await api.patch(`${endpoint}/${editing.id}`, form);
      } else {
        await api.post(endpoint, form);
      }
      setOpen(false);
      await load();
    } catch (e: any) {
      setErr(e?.response?.data?.detail ?? "Save failed");
    } finally {
      setBusy(false);
    }
  }

  async function remove(row: T) {
    if (!confirm(`Delete this ${title.toLowerCase().replace(/s$/, "")}?`)) return;
    await api.delete(`${endpoint}/${row.id}`);
    await load();
  }

  const cols: Column<T>[] = [
    ...columns,
    {
      key: "__actions",
      header: "",
      className: "w-32 text-right",
      render: (row) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="sm" onClick={() => openEdit(row)}><Pencil size={14} /></Button>
          <Button variant="ghost" size="sm" onClick={() => remove(row)}><Trash2 size={14} className="text-rose-600" /></Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">{title}</h1>
        <Button onClick={openCreate}><Plus size={16} /> New</Button>
      </div>

      <Card><CardContent><DataTable rows={rows} columns={cols} /></CardContent></Card>

      <Dialog
        open={open}
        onClose={() => setOpen(false)}
        title={editing ? `Edit ${title.replace(/s$/, "")}` : `New ${title.replace(/s$/, "")}`}
        footer={
          <>
            <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
            <Button onClick={save} disabled={busy}>{busy ? "Saving…" : "Save"}</Button>
          </>
        }
      >
        <div className="space-y-3">
          {fields.map((f) => (
            <FieldRow key={f.name} field={f} value={(form as any)[f.name]} onChange={(v) => setForm({ ...form, [f.name]: v } as Partial<T>)} />
          ))}
          {err && <div className="text-sm text-rose-600">{err}</div>}
        </div>
      </Dialog>
    </div>
  );
}

function FieldRow<T>({
  field, value, onChange,
}: { field: Field<T>; value: any; onChange: (v: any) => void }) {
  const id = `f-${String(field.name)}`;
  const common = "h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand/40 focus:border-brand";
  return (
    <div>
      <label htmlFor={id} className="block text-xs font-medium text-slate-600 mb-1">
        {field.label}{field.required ? " *" : ""}
      </label>
      {field.type === "textarea" ? (
        <textarea
          id={id}
          value={value ?? ""}
          onChange={(e) => onChange(e.target.value)}
          className={`${common} h-24 py-2`}
        />
      ) : (
        <input
          id={id}
          type={field.type ?? "text"}
          step={field.step}
          value={value ?? ""}
          onChange={(e) => onChange(field.type === "number" ? (e.target.value === "" ? null : Number(e.target.value)) : e.target.value)}
          className={common}
        />
      )}
    </div>
  );
}

