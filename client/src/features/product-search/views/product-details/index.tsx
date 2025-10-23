import { useCallback, useState } from "react";
import { get, isEmpty, isNumber, size } from "lodash";
import type { Product } from "../../types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import {
  TbTruck,
  TbShield,
  TbPackage,
  TbStar,
  TbWeight,
  TbRuler,
  TbBarcode,
  TbAlertCircle,
} from "react-icons/tb";
import { useChatStore } from "@/store/chat-store";

type ProductDetailsProps = {
  product: Product;
};

const ProductDetails = ({ product }: ProductDetailsProps) => {
  const { sendMessage } = useChatStore();
  const [selectedSize, setSelectedSize] = useState<string>("");
  const [selectedImage, setSelectedImage] = useState<string>("");

  const handleSend = useCallback(
    async (message: string) => {
      await sendMessage(message);
    },
    [sendMessage]
  );

  // Parse JSON fields properly
  const originalPrice = get(product, "price", 0);
  const discountPercentage = get(product, "discount_percentage", 0);
  const discountedPrice = originalPrice * (1 - discountPercentage / 100);

  // Safe JSON parsing with fallbacks
  const availableSizes = (() => {
    try {
      const sizesData = get(product, "available_sizes", "[]");
      return typeof sizesData === "string" ? JSON.parse(sizesData) : sizesData;
    } catch {
      return [];
    }
  })();

  const productImages = (() => {
    try {
      const imagesData = get(product, "images", "[]");
      return typeof imagesData === "string"
        ? JSON.parse(imagesData)
        : imagesData;
    } catch {
      return [];
    }
  })();

  const productTags = (() => {
    try {
      const tagsData = get(product, "tags", "[]");
      return typeof tagsData === "string" ? JSON.parse(tagsData) : tagsData;
    } catch {
      return [];
    }
  })();

  const productDimensions = (() => {
    try {
      const dimensionsData = get(product, "dimensions", "{}");
      return typeof dimensionsData === "string"
        ? JSON.parse(dimensionsData)
        : dimensionsData;
    } catch {
      return {};
    }
  })();

  // Set default selected image
  const mainImage =
    selectedImage || productImages[0] || get(product, "thumbnail", "");

  // Check if size selection is required
  const hasSizes = size(availableSizes) > 0;
  const isSizeRequired = hasSizes && !selectedSize;

  return (
    <div className="h-full w-full overflow-y-auto bg-background">
      <div className="max-w-2xl mx-auto px-3 sm:px-4 py-3 sm:py-4">
        {/* Main Content - Vertical Layout */}
        <div className="space-y-3 sm:space-y-4">
          {/* Product Images Section */}
          <div className="bg-card rounded-lg p-2 sm:p-3 border border-border">
            <div className="relative">
              <img
                className="w-full h-[280px] sm:h-[320px] object-cover rounded-md"
                src={mainImage}
                alt={get(product, "title", "Product")}
              />
              {discountPercentage > 0 && (
                <div className="absolute top-2 left-2 bg-destructive text-destructive-foreground px-2 py-0.5 rounded text-[10px] font-bold">
                  -{discountPercentage.toFixed(0)}%
                </div>
              )}
            </div>

            {/* Image Thumbnails */}
            {productImages.length > 1 && (
              <div className="flex gap-1.5 mt-2 overflow-x-auto pb-1">
                {productImages.map((image: string, index: number) => (
                  <img
                    key={index}
                    className={`w-14 h-14 object-cover rounded cursor-pointer transition-all flex-shrink-0 ${
                      selectedImage === image || (!selectedImage && index === 0)
                        ? "ring-2 ring-primary opacity-100"
                        : "opacity-60 hover:opacity-100"
                    }`}
                    src={image}
                    alt={`${get(product, "title", "Product")} ${index + 1}`}
                    onClick={() => setSelectedImage(image)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Product Info Section */}
          <div className="bg-card rounded-lg p-3 sm:p-4 border border-border space-y-3">
            <div>
              <div className="flex items-start justify-between gap-2 mb-1">
                <h1 className="text-lg sm:text-xl font-bold text-foreground leading-tight flex-1 line-clamp-2">
                  {get(product, "title", "Product Title")}
                </h1>
                <Badge
                  variant="outline"
                  className="capitalize text-[10px] flex-shrink-0 h-fit"
                >
                  {get(product, "category", "").replace("-", " ")}
                </Badge>
              </div>
              <p className="text-xs sm:text-sm font-medium text-primary mb-2">
                {get(product, "brand", "Unknown Brand")}
              </p>
              {!isEmpty(get(product, "description")) && (
                <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed line-clamp-3">
                  {get(product, "description")}
                </p>
              )}
            </div>

            {/* Price Section */}
            <div className="space-y-2">
              <div className="flex items-baseline gap-2 flex-wrap">
                {discountPercentage > 0 ? (
                  <>
                    <span className="text-xl sm:text-2xl font-bold text-chart-1">
                      ${discountedPrice.toFixed(2)}
                    </span>
                    <span className="text-base sm:text-lg text-muted-foreground line-through">
                      ${originalPrice.toFixed(2)}
                    </span>
                    <div className="bg-destructive text-destructive-foreground px-1.5 py-0.5 rounded text-[10px] font-semibold">
                      Save ${(originalPrice - discountedPrice).toFixed(2)}
                    </div>
                  </>
                ) : (
                  <span className="text-xl sm:text-2xl font-bold text-foreground">
                    ${originalPrice.toFixed(2)}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2 sm:gap-3 flex-wrap text-xs sm:text-sm">
                {isNumber(get(product, "rating")) &&
                  get(product, "rating", 0) > 0 && (
                    <div className="flex items-center gap-1">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <TbStar
                            key={i}
                            className={`w-3 h-3 sm:w-4 sm:h-4 ${
                              i < Math.floor(get(product, "rating", 0))
                                ? "text-chart-4 fill-current"
                                : "text-muted-foreground"
                            }`}
                          />
                        ))}
                      </div>
                      <span className="font-semibold text-foreground">
                        {get(product, "rating", 0).toFixed(1)}
                      </span>
                      <span className="text-muted-foreground">/5</span>
                    </div>
                  )}
                <span className="text-muted-foreground">
                  per {get(product, "unit", "piece")}
                </span>
              </div>
            </div>

            {/* Stock Status */}
            <div className="flex items-center gap-2">
              <TbPackage className="w-4 h-4 flex-shrink-0" />
              <Badge
                variant={
                  get(product, "availability_status") === "Out of Stock" ||
                  get(product, "stock", 0) === 0
                    ? "destructive"
                    : get(product, "availability_status") === "Low Stock" ||
                      (isNumber(get(product, "stock")) &&
                        get(product, "stock", 0) < 10)
                    ? "secondary"
                    : "default"
                }
                className="px-2 py-0.5 text-[10px]"
              >
                {get(product, "availability_status") === "Out of Stock" ||
                get(product, "stock", 0) === 0
                  ? "Out of Stock"
                  : `${get(product, "stock", 0)} in stock`}
              </Badge>
            </div>

            {/* Size Selection */}
            {size(availableSizes) > 0 && (
              <div className="space-y-2">
                <Label className="text-sm font-semibold">
                  Available Sizes:
                </Label>
                <RadioGroup
                  value={selectedSize}
                  onValueChange={setSelectedSize}
                  className="flex flex-wrap gap-1.5"
                >
                  {availableSizes.map((sizeOption: string) => (
                    <div key={sizeOption} className="flex items-center">
                      <RadioGroupItem
                        value={sizeOption}
                        id={`size-${sizeOption}`}
                        className="sr-only"
                      />
                      <Label
                        htmlFor={`size-${sizeOption}`}
                        className={`cursor-pointer px-3 py-1.5 border rounded transition-colors font-medium text-sm ${
                          selectedSize === sizeOption
                            ? "bg-primary text-primary-foreground border-primary"
                            : "hover:bg-accent hover:text-accent-foreground border-border"
                        }`}
                      >
                        {sizeOption}
                      </Label>
                    </div>
                  ))}
                </RadioGroup>
              </div>
            )}

            {/* Size Selection Validation Message */}
            {isSizeRequired && (
              <div className="flex items-center gap-2 p-3 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900 rounded-lg">
                <TbAlertCircle className="w-4 h-4 text-amber-600 dark:text-amber-500 flex-shrink-0" />
                <p className="text-xs sm:text-sm text-amber-800 dark:text-amber-400 font-medium">
                  Please select a size before proceeding
                </p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-2 pt-2">
              <Button
                className="flex-1 text-sm"
                variant="outline"
                onClick={() => {
                  const sizeText = selectedSize
                    ? ` in size ${selectedSize}`
                    : "";
                  const productTitle = get(product, "title", "this product");
                  const productBrand = get(product, "brand", "");
                  const prompt = `Add the ${productTitle} by ${productBrand}${sizeText} to my cart.`;
                  handleSend(prompt);
                }}
                disabled={
                  get(product, "availability_status") === "Out of Stock" ||
                  get(product, "stock", 0) === 0 ||
                  isSizeRequired
                }
              >
                Add to Cart
              </Button>
              <Button
                className="flex-1 text-sm"
                onClick={() => {
                  const sizeText = selectedSize
                    ? ` in size ${selectedSize}`
                    : "";
                  const productTitle = get(product, "title", "this product");
                  const productBrand = get(product, "brand", "");
                  const prompt = `I'd like to order the ${productTitle} by ${productBrand}${sizeText}.`;
                  handleSend(prompt);
                }}
                disabled={
                  get(product, "availability_status") === "Out of Stock" ||
                  get(product, "stock", 0) === 0 ||
                  isSizeRequired
                }
              >
                {get(product, "availability_status") === "Out of Stock" ||
                get(product, "stock", 0) === 0
                  ? "Out of Stock"
                  : "Buy Now"}
              </Button>
            </div>
          </div>

          {/* Product Details Section */}
          <div className="bg-card rounded-lg p-3 sm:p-4 border border-border space-y-3">
            <h2 className="text-base sm:text-lg font-bold text-foreground">
              Product Details
            </h2>

            <div className="grid grid-cols-2 gap-2">
              {!isEmpty(get(product, "sku")) && (
                <div className="bg-muted rounded-lg p-2 text-center">
                  <TbBarcode className="w-5 h-5 text-primary mx-auto mb-1" />
                  <div className="text-[10px] text-muted-foreground mb-0.5">
                    SKU
                  </div>
                  <div className="font-semibold text-[10px] break-all text-foreground">
                    {get(product, "sku")}
                  </div>
                </div>
              )}

              {isNumber(get(product, "weight")) &&
                get(product, "weight", 0) > 0 && (
                  <div className="bg-muted rounded-lg p-2 text-center">
                    <TbWeight className="w-5 h-5 text-primary mx-auto mb-1" />
                    <div className="text-[10px] text-muted-foreground mb-0.5">
                      Weight
                    </div>
                    <div className="font-semibold text-[10px] text-foreground">
                      {get(product, "weight", 0)} lbs
                    </div>
                  </div>
                )}

              {!isEmpty(productDimensions) && (
                <div className="bg-muted rounded-lg p-2 text-center">
                  <TbRuler className="w-5 h-5 text-primary mx-auto mb-1" />
                  <div className="text-[10px] text-muted-foreground mb-0.5">
                    Dimensions
                  </div>
                  <div className="font-semibold text-[9px] text-foreground">
                    {get(productDimensions, "width", 0)}" ×{" "}
                    {get(productDimensions, "height", 0)}" ×{" "}
                    {get(productDimensions, "depth", 0)}"
                  </div>
                </div>
              )}

              {isNumber(get(product, "minimum_order_quantity")) &&
                get(product, "minimum_order_quantity", 1) > 1 && (
                  <div className="bg-muted rounded-lg p-2 text-center">
                    <TbPackage className="w-5 h-5 text-primary mx-auto mb-1" />
                    <div className="text-[10px] text-muted-foreground mb-0.5">
                      Min. Order
                    </div>
                    <div className="font-semibold text-[10px] text-foreground">
                      {get(product, "minimum_order_quantity", 1)} units
                    </div>
                  </div>
                )}
            </div>

            {/* Tags Section */}
            {productTags.length > 0 && (
              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-foreground">Tags</h3>
                <div className="flex flex-wrap gap-1">
                  {productTags
                    .slice(0, 10)
                    .map((tag: string, index: number) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className="px-2 py-0.5 text-[10px]"
                      >
                        {tag}
                      </Badge>
                    ))}
                  {productTags.length > 10 && (
                    <Badge
                      variant="outline"
                      className="px-2 py-0.5 text-[10px]"
                    >
                      +{productTags.length - 10} more
                    </Badge>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Shipping and Returns Section */}
          {(!isEmpty(get(product, "shipping_information")) ||
            !isEmpty(get(product, "warranty_information")) ||
            !isEmpty(get(product, "return_policy"))) && (
            <div className="bg-card rounded-lg p-3 sm:p-4 border border-border space-y-3">
              <h2 className="text-base sm:text-lg font-bold text-foreground">
                Shipping & Returns
              </h2>

              <div className="grid grid-cols-1 gap-2">
                {!isEmpty(get(product, "shipping_information")) && (
                  <div className="bg-chart-2/10 rounded-lg p-2.5 text-center border border-chart-2/20">
                    <TbTruck className="w-5 h-5 text-chart-2 mx-auto mb-1" />
                    <div className="font-semibold text-xs text-foreground">
                      {get(product, "shipping_information").includes("1-2")
                        ? "Ships in 1-2 business days"
                        : get(product, "shipping_information")}
                    </div>
                  </div>
                )}

                {!isEmpty(get(product, "warranty_information")) && (
                  <div className="bg-chart-1/10 rounded-lg p-2.5 text-center border border-chart-1/20">
                    <TbShield className="w-5 h-5 text-chart-1 mx-auto mb-1" />
                    <div className="font-semibold text-xs text-foreground">
                      {get(product, "warranty_information") === "No warranty"
                        ? "No warranty"
                        : get(product, "warranty_information")}
                    </div>
                  </div>
                )}

                {!isEmpty(get(product, "return_policy")) && (
                  <div className="bg-chart-5/10 rounded-lg p-2.5 text-center border border-chart-5/20">
                    <TbPackage className="w-5 h-5 text-chart-5 mx-auto mb-1" />
                    <div className="font-semibold text-xs text-foreground">
                      {get(product, "return_policy").includes("60")
                        ? "60 days return policy"
                        : get(product, "return_policy")}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductDetails;
