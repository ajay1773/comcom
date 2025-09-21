import { useState, type FC } from "react";
import type { Product } from "../../types";
import ProductsList from "../products-list";
import ProductDetails from "../product-details";
import { Button } from "@/components/ui/button";
import { LuArrowLeft } from "react-icons/lu";

type ProductWindowProps = {
  products: Product[];
};

const ProductWindow: FC<ProductWindowProps> = ({ products }) => {
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const handleSelectProduct = (product: Product) => {
    setSelectedProduct(product);
  };

  return (
    <div className="w-full h-full">
      {selectedProduct ? (
        <div className="flex w-full h-full flex-col items-start justify-start gap-4">
          <Button variant={"ghost"} onClick={() => setSelectedProduct(null)}>
            <LuArrowLeft /> Back
          </Button>
          <ProductDetails product={selectedProduct} />
        </div>
      ) : (
        <ProductsList
          products={products}
          onSelectProduct={handleSelectProduct}
        />
      )}
    </div>
  );
};

export default ProductWindow;
