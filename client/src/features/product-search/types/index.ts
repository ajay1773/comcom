export type ProductCategory =
  | "electronics"
  | "clothing"
  | "beauty"
  | "home"
  | "sports"
  | "automotive";

export type Product = {
  id: number;
  title: string;
  description: string;
  category: ProductCategory;
  price: number;
  discount_percentage: number;
  rating: number;
  stock: number;
  tags: string[];
  brand: string;
  sku: string;
  weight: number;
  dimensions: {
    width: number;
    height: number;
    depth: number;
  };
  warranty_information: string;
  shipping_information: string;
  availability_status: string;
  return_policy: string;
  minimum_order_quantity: number;
  thumbnail: string;
  images: string;
  barcode: string;
  qr_code: string;
  available_sizes: string;
  unit: string;
  color?: string;
};
