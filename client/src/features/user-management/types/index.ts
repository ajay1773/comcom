export interface UserDetails {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserOrder {
  id: number;
  product_id: number;
  quantity: number;
  price: number;
  status: string;
  created_at: string;
  updated_at: string;
  product_name?: string;
  category?: string;
  brand?: string;
  color?: string;
  images?: string;
}

export interface UserAddress {
  id: number;
  type: string;
  street: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  is_default: boolean;
  full_address?: string;
}

export interface ProfileSummary {
  total_orders: number;
  total_addresses: number;
  account_status: string;
}

export interface UserProfileData {
  success_message: string;
  user_details: UserDetails;
  user_orders: UserOrder[];
  user_addresses: UserAddress[];
  profile_summary: ProfileSummary;
  suggested_actions: string[];
}
