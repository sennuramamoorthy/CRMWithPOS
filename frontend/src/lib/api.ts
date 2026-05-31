import axios from "axios";

export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: API_URL });

api.interceptors.request.use((cfg) => {
  const tok = localStorage.getItem("token");
  if (tok) cfg.headers.Authorization = `Bearer ${tok}`;
  return cfg;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem("token");
      if (!location.pathname.startsWith("/login")) location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export type Tenant = {
  id: number;
  slug: string;
  name: string;
  logo_url: string | null;
  primary_color: string;
};

export type User = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
};

export type Warehouse = {
  id: number;
  name: string;
  code: string;
  address?: string | null;
  city?: string | null;
  contact_name?: string | null;
  contact_phone?: string | null;
};

export type Distributor = {
  id: number;
  name: string;
  code: string;
  region?: string | null;
  contact_name?: string | null;
  contact_email?: string | null;
  contact_phone?: string | null;
  address?: string | null;
};

export type Product = {
  id: number;
  sku: string;
  name: string;
  description?: string | null;
  unit: string;
  price: string;
  cost: string;
  distributor_id?: number | null;
};

export type StockLevel = {
  id: number;
  warehouse_id: number;
  product_id: number;
  quantity: number;
};

export type Customer = {
  id: number;
  name: string;
  email?: string | null;
  phone?: string | null;
  company?: string | null;
  address?: string | null;
  notes?: string | null;
};

export type OrderItem = {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: string;
  line_total: string;
};

export type Order = {
  id: number;
  code: string;
  customer_id: number | null;
  warehouse_id: number;
  status: string;
  subtotal: string;
  tax: string;
  discount: string;
  total: string;
  created_at: string;
  items: OrderItem[];
};

export type Invoice = {
  id: number;
  number: string;
  order_id: number;
  customer_id: number | null;
  total: string;
  amount_paid: string;
  status: string;
  issued_at: string;
  due_at: string | null;
};

export type Payment = {
  id: number;
  invoice_id: number;
  amount: string;
  method: string;
  reference?: string | null;
  note?: string | null;
  created_at: string;
};

export type Summary = {
  total_customers: number;
  total_products: number;
  total_warehouses: number;
  total_distributors: number;
  revenue_30d: string;
  outstanding: string;
  orders_30d: number;
  low_stock_count: number;
};

export type DailyRevenuePoint = { date: string; revenue: string; orders: number };
