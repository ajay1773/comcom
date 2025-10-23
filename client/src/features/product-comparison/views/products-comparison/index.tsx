import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import {
  TbArrowsSort,
  TbStar,
  TbPackage,
  TbTrendingUp,
  TbTrendingDown,
  TbShoppingCart,
} from "react-icons/tb";
import type { ProductComparisonPayload } from "../../types";

type Props = {
  payload: ProductComparisonPayload;
};

const ProductsComparison = ({ payload }: Props) => {
  const {
    products,
    comparison_table,
    product_count,
    criteria_used,
    category_mismatch_warning,
    categories,
  } = payload;

  // Parse image URLs (handle JSON string format)
  const parseImageUrl = (imageUrl: string): string => {
    try {
      if (imageUrl.startsWith("[")) {
        const parsed = JSON.parse(imageUrl);
        return Array.isArray(parsed) && parsed.length > 0 ? parsed[0] : "";
      }
      return imageUrl;
    } catch {
      return imageUrl;
    }
  };

  // Get price comparison indicator
  const getPriceComparison = (index: number) => {
    if (!products || products.length < 2) return null;
    const prices = products.map((p) => p.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);

    if (products[index].price === minPrice && minPrice !== maxPrice) {
      return { label: "Best Price", variant: "success", icon: TbTrendingDown };
    }
    if (products[index].price === maxPrice && minPrice !== maxPrice) {
      return { label: "Highest", variant: "secondary", icon: TbTrendingUp };
    }
    return null;
  };

  // Get rating comparison indicator
  const getRatingComparison = (index: number) => {
    if (!products || products.length < 2) return null;
    const ratings = products.map((p) => p.rating);
    const maxRating = Math.max(...ratings);
    const minRating = Math.min(...ratings);

    if (products[index].rating === maxRating && minRating !== maxRating) {
      return { label: "Top Rated", variant: "success" };
    }
    return null;
  };

  return (
    <div className="w-full space-y-3 sm:space-y-4 py-2 px-2 sm:px-0">
      {/* Category Mismatch Warning */}
      {category_mismatch_warning && categories && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 sm:p-4">
          <div className="flex items-start gap-2 sm:gap-3">
            <div className="flex-shrink-0">
              <svg
                className="h-4 w-4 sm:h-5 sm:w-5 text-yellow-600"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="flex-1">
              <h4 className="text-xs sm:text-sm font-medium text-yellow-800">
                Different Categories Detected
              </h4>
              <p className="text-xs sm:text-sm text-yellow-700 mt-1">
                These products are from different categories (
                {categories.join(", ")}). While they can still be compared, keep
                in mind they serve different purposes.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Header Section */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-1.5 sm:gap-2">
          <TbArrowsSort className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
          <h3 className="text-sm sm:text-base font-semibold">
            Comparing {product_count} Products
          </h3>
        </div>
        {criteria_used && criteria_used.length > 0 && (
          <Badge variant="outline" className="text-[10px] sm:text-xs">
            {criteria_used.length} criteria
          </Badge>
        )}
      </div>

      {/* Product Cards Carousel */}
      <Carousel
        opts={{
          align: "start",
          loop: false,
        }}
        className="w-full"
      >
        <CarouselContent className="-ml-1 sm:-ml-2">
          {products.map((product, index) => {
            const priceIndicator = getPriceComparison(index);
            const ratingIndicator = getRatingComparison(index);
            const imageUrl = parseImageUrl(product.images);
            const hasDiscount = product.discount > 0;
            const finalPrice = hasDiscount
              ? product.price * (1 - product.discount / 100)
              : product.price;

            return (
              <CarouselItem
                key={product.id}
                className="pl-1 sm:pl-2 basis-[90%] sm:basis-[85%] md:basis-[45%] lg:basis-[32%]"
              >
                <Card className="overflow-hidden hover:shadow-md transition-shadow">
                  <div className="relative">
                    <img
                      src={imageUrl || "/placeholder.png"}
                      alt={product.name}
                      className="w-full h-28 sm:h-32 md:h-36 object-cover bg-muted"
                      onError={(e) => {
                        e.currentTarget.src = "/placeholder.png";
                      }}
                    />
                    {hasDiscount && (
                      <Badge
                        variant="destructive"
                        className="absolute top-1.5 sm:top-2 right-1.5 sm:right-2 text-[10px] sm:text-xs"
                      >
                        -{product.discount.toFixed(0)}%
                      </Badge>
                    )}
                    {priceIndicator && (
                      <Badge
                        variant={
                          priceIndicator.variant === "success"
                            ? "default"
                            : "secondary"
                        }
                        className={`absolute top-1.5 sm:top-2 left-1.5 sm:left-2 text-[10px] sm:text-xs flex items-center gap-0.5 sm:gap-1 ${
                          priceIndicator.variant === "success"
                            ? "bg-green-500 hover:bg-green-600"
                            : ""
                        }`}
                      >
                        <priceIndicator.icon className="h-2.5 w-2.5 sm:h-3 sm:w-3" />
                        {priceIndicator.label}
                      </Badge>
                    )}
                  </div>

                  <CardContent className="p-2 sm:p-3 space-y-1.5 sm:space-y-2">
                    {/* Brand and Category */}
                    <div className="flex items-center justify-between gap-1">
                      <span className="text-[10px] sm:text-xs font-medium text-primary truncate">
                        {product.brand}
                      </span>
                      <Badge
                        variant="outline"
                        className="text-[9px] sm:text-xs capitalize shrink-0"
                      >
                        {product.category}
                      </Badge>
                    </div>

                    {/* Product Name */}
                    <h4 className="text-xs sm:text-sm font-medium line-clamp-2 leading-tight min-h-[2rem] sm:min-h-[2.5rem]">
                      {product.name}
                    </h4>

                    {/* Price */}
                    <div className="flex items-baseline gap-1.5 sm:gap-2">
                      {hasDiscount ? (
                        <>
                          <span className="text-base sm:text-lg font-bold text-green-600">
                            ${finalPrice.toFixed(2)}
                          </span>
                          <span className="text-[10px] sm:text-xs text-muted-foreground line-through">
                            ${product.price.toFixed(2)}
                          </span>
                        </>
                      ) : (
                        <span className="text-base sm:text-lg font-bold">
                          ${product.price.toFixed(2)}
                        </span>
                      )}
                    </div>

                    {/* Rating and Stock */}
                    <div className="flex items-center justify-between text-[10px] sm:text-xs">
                      <div className="flex items-center gap-0.5 sm:gap-1">
                        <TbStar className="h-3 w-3 sm:h-3.5 sm:w-3.5 text-yellow-500 fill-yellow-500" />
                        <span className="font-medium">
                          {product.rating.toFixed(1)}
                        </span>
                        {ratingIndicator && (
                          <Badge
                            variant="outline"
                            className="ml-0.5 sm:ml-1 text-[8px] sm:text-[10px] px-0.5 sm:px-1 py-0 h-3 sm:h-4 bg-green-50 text-green-700 border-green-200 dark:bg-green-950 dark:text-green-400 dark:border-green-800"
                          >
                            {ratingIndicator.label}
                          </Badge>
                        )}
                      </div>
                      <div className="flex items-center gap-0.5 sm:gap-1 text-muted-foreground">
                        <TbPackage className="h-3 w-3 sm:h-3.5 sm:w-3.5" />
                        <span>{product.stock > 0 ? "In Stock" : "Out"}</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </CarouselItem>
            );
          })}
        </CarouselContent>
        {product_count > 1 && (
          <>
            <CarouselPrevious className="-left-2 sm:-left-3 h-6 w-6 sm:h-7 sm:w-7" />
            <CarouselNext className="-right-2 sm:-right-3 h-6 w-6 sm:h-7 sm:w-7" />
          </>
        )}
      </Carousel>

      <Separator />

      {/* Quick Comparison Table */}
      <div className="space-y-1 overflow-x-auto">
        <h4 className="text-xs sm:text-sm font-semibold mb-1.5 sm:mb-2 flex items-center gap-1.5 sm:gap-2">
          <TbArrowsSort className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
          Quick Comparison
        </h4>
        <div className="space-y-0.5 sm:space-y-1 min-w-[300px]">
          {Object.entries(comparison_table).map(([attribute, values]) => (
            <div
              key={attribute}
              className="grid gap-1.5 sm:gap-2 py-1.5 sm:py-2 px-2 sm:px-3 rounded-md hover:bg-muted/50 transition-colors"
              style={{
                gridTemplateColumns: `minmax(70px, 0.8fr) repeat(${product_count}, 1fr)`,
              }}
            >
              <div className="font-medium text-[10px] sm:text-xs text-muted-foreground flex items-center">
                {attribute}
              </div>
              {values.map((value, idx) => {
                // Determine if this is the best value for highlighting
                const isBestPrice =
                  attribute === "Price" &&
                  products.length > 1 &&
                  products[idx].price ===
                    Math.min(...products.map((p) => p.price));

                const isBestRating =
                  attribute === "Rating" &&
                  products.length > 1 &&
                  products[idx].rating ===
                    Math.max(...products.map((p) => p.rating));

                return (
                  <div
                    key={idx}
                    className={`text-[10px] sm:text-xs font-medium px-1.5 sm:px-2 py-1 rounded ${
                      isBestPrice || isBestRating
                        ? "bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-300"
                        : ""
                    }`}
                  >
                    {value}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Criteria Used */}
      {criteria_used && criteria_used.length > 0 && (
        <>
          <Separator />
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="criteria" className="border-none">
              <AccordionTrigger className="text-xs sm:text-sm font-semibold hover:no-underline py-1.5 sm:py-2">
                <span className="flex items-center gap-1.5 sm:gap-2">
                  Comparison Criteria ({criteria_used.length})
                </span>
              </AccordionTrigger>
              <AccordionContent>
                <div className="flex flex-wrap gap-1.5 sm:gap-2 pt-1">
                  {criteria_used.map((criterion, idx) => (
                    <Badge
                      key={idx}
                      variant="secondary"
                      className="text-[10px] sm:text-xs capitalize"
                    >
                      {criterion}
                    </Badge>
                  ))}
                </div>
                <p className="text-[10px] sm:text-xs text-muted-foreground mt-2 sm:mt-3">
                  Products are compared based on the criteria above. The AI
                  analysis considers these factors to provide comprehensive
                  insights.
                </p>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </>
      )}

      {/* Quick Actions Footer */}
      <div className="flex items-center gap-1.5 sm:gap-2 pt-1.5 sm:pt-2">
        <div className="flex items-center gap-0.5 sm:gap-1 text-[10px] sm:text-xs text-muted-foreground">
          <TbShoppingCart className="h-3 w-3 sm:h-3.5 sm:w-3.5" />
          <span>Scroll through products above to view details</span>
        </div>
      </div>
    </div>
  );
};

export default ProductsComparison;
