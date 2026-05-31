import { CrudPage, Field } from "@/components/CrudPage";
import { Customer } from "@/lib/api";

const fields: Field<Customer>[] = [
  { name: "name", label: "Name", required: true },
  { name: "email", label: "Email" },
  { name: "phone", label: "Phone" },
  { name: "company", label: "Company" },
  { name: "address", label: "Address" },
  { name: "notes", label: "Notes", type: "textarea" },
];

export function CustomersPage() {
  return (
    <CrudPage<Customer>
      title="Customers"
      endpoint="/customers"
      fields={fields}
      emptyDefaults={{ name: "" }}
      columns={[
        { key: "name", header: "Name" },
        { key: "company", header: "Company" },
        { key: "email", header: "Email" },
        { key: "phone", header: "Phone" },
      ]}
    />
  );
}
