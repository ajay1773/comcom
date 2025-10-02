import type { UserAddress } from "@/features/user-management/types";

export type CartItem = {
  id: number;
  product_id: number;
  quantity: number;
  unit_price: number;
  total_price: number;
  size?: string;
  color?: string;
  unit?: string;
  selected_options?: string;
  added_at: string;
  updated_at: string;
};

export type CartItemWithProductDetails = CartItem & {
  product_details: {
    id: number;
    name: string;
    category: string;
    price: number;
    gender: string;
    brand: string;
    material: string;
    style: string;
    pattern: string;
    color: string;
    images: {
      thumbnail: string;
      preview: string;
      full: string;
    };
    available_sizes: string[];
    unit: string;
  };
};

export type AddToCartSuccess = {
  message: unknown;
  cart_items: CartItem[];
  suggested_actions: unknown;
};

export type CartDetails = {
  message: {
    type: string;
    text: string;
  };
  cart_items: CartItemWithProductDetails[];
  cart_summary: {
    item_count: number;
    total_items: number;
    total_value: number;
  };
  suggested_actions: unknown;
};

export type CheckoutUIProviderData = {
  product_items: CartItemWithProductDetails[];
  saved_addresses: UserAddress[];
  allowed_payment_methods: string[];
  total_amount: number;
};
