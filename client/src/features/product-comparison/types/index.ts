export type ComparisonProduct = {
  id: number;
  name: string;
  brand: string;
  price: number;
  rating: number;
  images: string;
  stock: number;
  discount: number;
  category: string;
};

export type ProductComparisonPayload = {
  products: ComparisonProduct[];
  comparison_table: Record<string, string[]>;
  product_count: number;
  criteria_used: string[];
  category_mismatch_warning?: boolean;
  categories?: string[];
};

export type StatusCardPayload = {
  title: string;
  subtitle: string;
  message: string;
  icon: string;
  actions?: Array<{
    type: string;
    label: string;
    action: string;
  }>;
  suggestions?: string[];
  products?: Array<{
    id: number;
    name: string;
    category?: string;
    brand?: string;
    price?: number;
  }>;
};
