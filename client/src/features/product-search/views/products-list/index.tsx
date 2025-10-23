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
    return <IconComponent className="w-3 h-3 sm:w-4 sm:h-4" />;
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
        <div className="flex w-full flex-wrap gap-2 sm:gap-3 md:gap-4 h-full overflow-y-auto items-start px-1 sm:px-0">
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
                className="py-0 gap-2 sm:gap-3 md:gap-4 flex-none w-full sm:w-[calc(50%-0.375rem)] md:w-[calc(50%-0.5rem)] hover:shadow-lg transition-shadow"
                key={defaultTo(get(product, "id"), index)}
              >
                <div className="relative bg-white rounded-t-lg sm:rounded-t-xl">
                  <img
                    className="w-full h-32 sm:h-40 md:h-48 object-contain rounded-t-lg sm:rounded-t-xl"
                    src={defaultTo(
                      productImages[0],
                      defaultTo(get(product, "thumbnail"), "")
                    )}
                    alt={get(product, "title", "")}
                  />
                  {discountPercentage > 0 && (
                    <Badge
                      className="absolute top-1.5 right-1.5 sm:top-2 sm:right-2 bg-red-500 text-white text-[10px] sm:text-xs px-1.5 sm:px-2 py-0.5"
                      variant="destructive"
                    >
                      -{discountPercentage}%
                    </Badge>
                  )}
                </div>

                <CardContent className="flex flex-col items-start justify-start px-2.5 sm:px-3 md:px-4 pb-1.5 sm:pb-2">
                  <div className="flex flex-col gap-1.5 sm:gap-2 items-start justify-start w-full">
                    {/* Brand and Category */}
                    <div className="flex items-center justify-between w-full">
                      <span className="text-[10px] sm:text-xs font-medium text-blue-600 truncate max-w-[60%]">
                        {get(product, "brand", "")}
                      </span>
                      {/* Hide category badge on mobile */}
                      <Badge
                        variant="outline"
                        className="hidden sm:flex items-center gap-1"
                      >
                        {getCategoryIcon(get(product, "category", ""))}
                        <span className="text-xs capitalize">
                          {get(product, "category", "")}
                        </span>
                      </Badge>
                    </div>

                    {/* Product Title */}
                    <h3 className="text-xs sm:text-sm font-medium line-clamp-2 leading-tight">
                      {get(product, "title", "")}
                    </h3>

                    {/* Price */}
                    <div className="flex items-center gap-1.5 sm:gap-2">
                      {discountPercentage > 0 ? (
                        <>
                          <span className="text-sm sm:text-base md:text-lg font-bold text-green-600">
                            $
                            {isNumber(discountedPrice)
                              ? discountedPrice.toFixed(2)
                              : "0.00"}
                          </span>
                          <span className="text-[10px] sm:text-xs md:text-sm text-muted-foreground line-through">
                            $
                            {isNumber(originalPrice)
                              ? originalPrice.toFixed(2)
                              : "0.00"}
                          </span>
                        </>
                      ) : (
                        <span className="text-sm sm:text-base md:text-lg font-bold">
                          $
                          {isNumber(originalPrice)
                            ? originalPrice.toFixed(2)
                            : "0.00"}
                        </span>
                      )}
                      {/* Hide unit on mobile */}
                      <span className="hidden sm:inline text-xs text-muted-foreground">
                        per {get(product, "unit", "item")}
                      </span>
                    </div>

                    {/* Rating and Stock */}
                    <div className="flex items-center justify-between w-full">
                      {get(product, "rating", 0) > 0 && (
                        <div className="flex items-center gap-0.5 sm:gap-1">
                          <span className="text-yellow-500 text-xs sm:text-sm">
                            ⭐
                          </span>
                          <span className="text-[10px] sm:text-xs font-medium">
                            {isNumber(get(product, "rating"))
                              ? get(product, "rating").toFixed(1)
                              : "0.0"}
                          </span>
                          <span className="text-[10px] sm:text-xs text-muted-foreground">
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
                          className="text-[9px] sm:text-[10px] md:text-xs px-1.5 sm:px-2 py-0.5"
                        >
                          {getStockText(
                            get(product, "stock", 0),
                            get(product, "availability_status", "")
                          )}
                        </Badge>
                      )}
                    </div>

                    {/* Sizes - Hidden on mobile */}
                    {has(product, "available_sizes") &&
                      !isEmpty(get(product, "available_sizes")) && (
                        <p className="hidden sm:block text-xs text-muted-foreground">
                          Sizes:{" "}
                          {join(
                            slice(get(product, "available_sizes"), 0, 3),
                            ", "
                          )}
                          {get(product, "available_sizes", []).length > 3 &&
                            " +more"}
                        </p>
                      )}

                    {/* SKU - Hidden on mobile */}
                    {has(product, "sku") && get(product, "sku") && (
                      <p className="hidden sm:block text-xs text-muted-foreground">
                        SKU: {get(product, "sku")}
                      </p>
                    )}
                  </div>
                </CardContent>

                <CardFooter className="flex items-center flex-col gap-2 justify-between w-full px-2.5 sm:px-3 md:px-4 pb-2.5 sm:pb-3 md:pb-4 pt-0">
                  <Button
                    className="w-full text-xs sm:text-sm h-8 sm:h-9 md:h-10"
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
