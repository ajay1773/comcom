import { useState, type FC } from "react";
import type { Product } from "../../types";
import ProductsList from "../products-list";
import ProductDetails from "../product-details";
import { Button } from "@/components/ui/button";
import { LuArrowLeft } from "react-icons/lu";

export type ProductWindowProps = {
  payload: {
    products: Product[];
    search_parameters: {
      query: string;
      category: string;
      price_range: string;
      color: string;
      brand: string;
    };
    result_count: number;
    success_message: string;
  };
};

const ProductWindow: FC<ProductWindowProps> = ({ payload }) => {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const handleSelectProduct = (product: Product) => {
    setSelectedProduct(product);
  };

  return (
    <div className="w-full h-full">
      {selectedProduct ? (
        <div className="flex w-full h-full flex-col items-start justify-start overflow-y-auto">
          <div className="sticky top-0 z-10 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border w-full px-3 sm:px-4 py-2">
            <Button
              variant="ghost"
              onClick={() => setSelectedProduct(null)}
              className="gap-2 hover:gap-3 transition-all"
              size="sm"
            >
              <LuArrowLeft className="w-4 h-4" />
              <span>Back to Results</span>
            </Button>
          </div>
          <ProductDetails product={selectedProduct} />
        </div>
      ) : (
        <ProductsList
          products={payload.products}
          onSelectProduct={handleSelectProduct}
        />
      )}
    </div>
  );
};

export default ProductWindow;
