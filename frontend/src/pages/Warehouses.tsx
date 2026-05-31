import { CrudPage, Field } from "@/components/CrudPage";
import { Warehouse } from "@/lib/api";

const fields: Field<Warehouse>[] = [
  { name: "name", label: "Name", required: true },
  { name: "code", label: "Code", required: true },
  { name: "address", label: "Address" },
  { name: "city", label: "City" },
  { name: "contact_name", label: "Contact name" },
  { name: "contact_phone", label: "Contact phone" },
];

export function WarehousesPage() {
  return (
    <CrudPage<Warehouse>
      title="Warehouses"
      endpoint="/warehouses"
      fields={fields}
      emptyDefaults={{ name: "", code: "" }}
      columns={[
        { key: "code", header: "Code" },
        { key: "name", header: "Name" },
        { key: "city", header: "City" },
        { key: "contact_name", header: "Contact" },
        { key: "contact_phone", header: "Phone" },
      ]}
    />
  );
}
