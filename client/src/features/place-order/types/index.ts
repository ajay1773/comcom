import type { Product } from "@/features/product-search/types";

export type OrderDetails = {
  selected_product: Product;
  addresses: Address[];
  price_breakdown: PriceBreakdown;
};

export type PriceBreakdown = {
  subtotal: number;
  shipping: number;
  tax: number;
  total: number;
};

export type Address = {
  id: string;
  name: string;
  street: string;
  city: string;
  state: string;
  zip: string;
  country: string;
  is_default: boolean;
};

export type PaymentDetails = {
  selected_product: Product;
  price_breakdown: PriceBreakdown;
};

export type PaymentStatusDetails = {
  selected_product: Product;
  price_breakdown: PriceBreakdown;
  transaction_details: TransactionDetails;
};

export type TransactionDetails = {
  transaction_id: string;
  transaction_date: string;
  transaction_type: string;
  transaction_status: string;
  transaction_amount: number;
};
