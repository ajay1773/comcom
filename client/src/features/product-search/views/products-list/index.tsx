import { Button } from "@/components/ui/button";
import type { Product } from "../../types";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { isEmpty, get, has, defaultTo, isNumber, slice, join } from "lodash";
import {
  TbDeviceLaptop,
  TbShirt,
  TbSparkles,
  TbHome,
  TbBallBasketball,
  TbCar,
  TbShoe,
  TbShoppingBag,
  TbDiamond,
  TbCategory,
} from "react-icons/tb";

type ProductsListProps = {
  products: Product[];
  onSelectProduct: (product: Product) => void;
};

// Category icons mapping
const CATEGORY_ICONS = {
  electronics: TbDeviceLaptop,
  clothing: TbShirt,
  beauty: TbSparkles,
  home: TbHome,
  sports: TbBallBasketball,
  automotive: TbCar,
  shoes: TbShoe,
  accessories: TbCategory,
  bags: TbShoppingBag,
  jewelry: TbDiamond,
  other: TbCategory,
} as const;

const ProductsList = ({ products, onSelectProduct }: ProductsListProps) => {
  const getCategoryIcon = (category: string) => {
    const IconComponent = get(CATEGORY_ICONS, category, TbCategory);
    return <IconComponent className="w-4 h-4" />;
  };

  const getStockBadgeVariant = (stock: number, availabilityStatus: string) => {
    const safeStock = defaultTo(stock, 0);
    const safeStatus = defaultTo(availabilityStatus, "");

    if (safeStatus === "Out of Stock" || safeStock === 0) {
      return "destructive";
    }
    if (safeStatus === "Low Stock" || safeStock < 10) {
      return "secondary";
    }
    return "default";
  };

  const getStockText = (stock: number, availabilityStatus: string) => {
    const safeStock = defaultTo(stock, 0);
    const safeStatus = defaultTo(availabilityStatus, "");

    if (safeStatus === "Out of Stock" || safeStock === 0) {
      return "Out of Stock";
    }
    if (safeStatus === "Low Stock" || safeStock < 10) {
      return `Low Stock (${safeStock})`;
    }
    return `${safeStock} in stock`;
  };

  return (
    <>
      {!isEmpty(products) && (
        <div className="flex w-full flex-wrap gap-4 h-full overflow-y-auto items-start">
          {products.map((product, index) => {
            const originalPrice = defaultTo(get(product, "price"), 0);
            const discountPercentage = defaultTo(
              get(product, "discount_percentage"),
              0
            );
            const discountedPrice =
              originalPrice * (1 - discountPercentage / 100);

            const imagesData = get(product, "images", "[]");
            const productImages =
              typeof imagesData === "string"
                ? (JSON.parse(imagesData) as string[])
                : (imagesData as string[]);

            return (
              <Card
                className="py-0 gap-4 flex-none w-[calc(50%-0.5rem)] hover:shadow-lg transition-shadow"
                key={defaultTo(get(product, "id"), index)}
              >
                <div className="relative">
                  <img
                    className="w-full h-48 object-cover rounded-t-xl"
                    src={defaultTo(
                      productImages[0],
                      defaultTo(get(product, "thumbnail"), "")
                    )}
                    alt={get(product, "title", "")}
                  />
                  {discountPercentage > 0 && (
                    <Badge
                      className="absolute top-2 right-2 bg-red-500 text-white"
                      variant="destructive"
                    >
                      -{discountPercentage}%
                    </Badge>
                  )}
                </div>

                <CardContent className="flex flex-col items-start justify-start px-4 pb-2">
                  <div className="flex flex-col gap-2 items-start justify-start w-full">
                    {/* Brand and Category */}
                    <div className="flex items-center justify-between w-full">
                      <span className="text-xs font-medium text-blue-600">
                        {get(product, "brand", "")}
                      </span>
                      <Badge
                        variant="outline"
                        className="flex items-center gap-1"
                      >
                        {getCategoryIcon(get(product, "category", ""))}
                        <span className="text-xs capitalize">
                          {get(product, "category", "")}
                        </span>
                      </Badge>
                    </div>

                    {/* Product Title */}
                    <h3 className="text-sm font-medium line-clamp-2 leading-tight">
                      {get(product, "title", "")}
                    </h3>

                    {/* Price */}
                    <div className="flex items-center gap-2">
                      {discountPercentage > 0 ? (
                        <>
                          <span className="text-lg font-bold text-green-600">
                            $
                            {isNumber(discountedPrice)
                              ? discountedPrice.toFixed(2)
                              : "0.00"}
                          </span>
                          <span className="text-sm text-muted-foreground line-through">
                            $
                            {isNumber(originalPrice)
                              ? originalPrice.toFixed(2)
                              : "0.00"}
                          </span>
                        </>
                      ) : (
                        <span className="text-lg font-bold">
                          $
                          {isNumber(originalPrice)
                            ? originalPrice.toFixed(2)
                            : "0.00"}
                        </span>
                      )}
                      <span className="text-xs text-muted-foreground">
                        per {get(product, "unit", "item")}
                      </span>
                    </div>

                    {/* Rating and Stock */}
                    <div className="flex items-center justify-between w-full">
                      {get(product, "rating", 0) > 0 && (
                        <div className="flex items-center gap-1">
                          <span className="text-yellow-500">⭐</span>
                          <span className="text-xs font-medium">
                            {isNumber(get(product, "rating"))
                              ? get(product, "rating").toFixed(1)
                              : "0.0"}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            /5
                          </span>
                        </div>
                      )}

                      {(has(product, "stock") ||
                        has(product, "availability_status")) && (
                        <Badge
                          variant={getStockBadgeVariant(
                            get(product, "stock", 0),
                            get(product, "availability_status", "")
                          )}
                          className="text-xs"
                        >
                          {getStockText(
                            get(product, "stock", 0),
                            get(product, "availability_status", "")
                          )}
                        </Badge>
                      )}
                    </div>

                    {/* Sizes */}
                    {has(product, "available_sizes") &&
                      !isEmpty(get(product, "available_sizes")) && (
                        <p className="text-xs text-muted-foreground">
                          Sizes:{" "}
                          {join(
                            slice(get(product, "available_sizes"), 0, 3),
                            ", "
                          )}
                          {get(product, "available_sizes", []).length > 3 &&
                            " +more"}
                        </p>
                      )}

                    {/* SKU */}
                    {has(product, "sku") && get(product, "sku") && (
                      <p className="text-xs text-muted-foreground">
                        SKU: {get(product, "sku")}
                      </p>
                    )}
                  </div>
                </CardContent>

                <CardFooter className="flex items-center flex-col gap-2 justify-between w-full p-4 pt-0">
                  <Button
                    className="w-full"
                    variant={"default"}
                    onClick={() => {
                      onSelectProduct(product);
                    }}
                    disabled={
                      get(product, "availability_status") === "Out of Stock" ||
                      get(product, "stock", 0) === 0
                    }
                  >
                    {get(product, "availability_status") === "Out of Stock" ||
                    get(product, "stock", 0) === 0
                      ? "Out of Stock"
                      : "View Details"}
                  </Button>
                </CardFooter>
              </Card>
            );
          })}
        </div>
      )}
    </>
  );
};

export default ProductsList;
