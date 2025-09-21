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

export type AddToCartSuccess = {
  message: unknown;
  cart_details: CartItem[];
  suggested_actions: unknown;
};
