import { CrudPage, Field } from "@/components/CrudPage";
import { Distributor } from "@/lib/api";

const fields: Field<Distributor>[] = [
  { name: "name", label: "Name", required: true },
  { name: "code", label: "Code", required: true },
  { name: "region", label: "Region" },
  { name: "contact_name", label: "Contact name" },
  { name: "contact_email", label: "Contact email" },
  { name: "contact_phone", label: "Contact phone" },
  { name: "address", label: "Address" },
];

export function DistributorsPage() {
  return (
    <CrudPage<Distributor>
      title="Distributors"
      endpoint="/distributors"
      fields={fields}
      emptyDefaults={{ name: "", code: "" }}
      columns={[
        { key: "code", header: "Code" },
        { key: "name", header: "Name" },
        { key: "region", header: "Region" },
        { key: "contact_name", header: "Contact" },
        { key: "contact_email", header: "Email" },
      ]}
    />
  );
}
