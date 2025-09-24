export type ProductCategory =
  | "accessories"
  | "bags"
  | "clothing"
  | "jewelry"
  | "shoes"
  | "other";

export type Product = {
  id?: number;
  name: string;
  gender: string;
  category: ProductCategory;
  min_price: number;
  max_price: number;
  color: string;
  brand: string;
  material: string;
  style: string;
  pattern: string;
  images: ProductImage;
  available_sizes: string[];
  unit: string;
};
export type ProductImage = {
  thumbnail: string;
  preview: string;
  full: string;
};
