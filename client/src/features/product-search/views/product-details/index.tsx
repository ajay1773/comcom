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
  TbArrowLeft,
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

  const handleBack = () => {
    window.history.back();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-card border-b border-border">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBack}
                className="flex items-center gap-2"
              >
                <TbArrowLeft className="w-4 h-4" />
                Back
              </Button>
              <span className="text-sm text-muted-foreground">
                {get(product, "category", "").replace("-", " ")}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold text-primary">
                {get(product, "brand", "Unknown Brand")}
              </span>
              <Badge variant="outline" className="capitalize">
                {get(product, "category", "").replace("-", " ")}
              </Badge>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Main Content - Vertical Layout */}
        <div className="space-y-8">
          {/* Product Images Section */}
          <div className="bg-card rounded-2xl p-6 shadow-sm border border-border">
            <div className="relative">
              <img
                className="w-full h-80 object-cover rounded-xl"
                src={mainImage}
                alt={get(product, "title", "Product")}
              />
              {discountPercentage > 0 && (
                <div className="absolute top-4 left-4 bg-destructive text-destructive-foreground px-3 py-1 rounded-lg font-semibold">
                  -{discountPercentage.toFixed(2)}%
                </div>
              )}
            </div>

            {/* Image Thumbnails */}
            {productImages.length > 1 && (
              <div className="flex gap-3 mt-4 overflow-x-auto pb-2">
                {productImages.map((image: string, index: number) => (
                  <img
                    key={index}
                    className={`w-16 h-16 object-cover rounded-lg cursor-pointer transition-all ${
                      selectedImage === image || (!selectedImage && index === 0)
                        ? "ring-2 ring-primary opacity-100"
                        : "opacity-70 hover:opacity-100"
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
          <div className="bg-card rounded-2xl p-6 shadow-sm border border-border space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-foreground leading-tight">
                {get(product, "title", "Product Title")}
              </h1>
              {!isEmpty(get(product, "description")) && (
                <p className="text-muted-foreground mt-3 leading-relaxed">
                  {get(product, "description")}
                </p>
              )}
            </div>

            {/* Price Section */}
            <div className="space-y-3">
              <div className="flex items-baseline gap-4">
                {discountPercentage > 0 ? (
                  <>
                    <span className="text-3xl font-bold text-chart-1">
                      ${discountedPrice.toFixed(2)}
                    </span>
                    <span className="text-xl text-muted-foreground line-through">
                      ${originalPrice.toFixed(2)}
                    </span>
                    <div className="bg-destructive text-destructive-foreground px-3 py-1 rounded-lg text-sm font-semibold">
                      Save ${(originalPrice - discountedPrice).toFixed(2)}
                    </div>
                  </>
                ) : (
                  <span className="text-3xl font-bold text-foreground">
                    ${originalPrice.toFixed(2)}
                  </span>
                )}
              </div>

              <div className="flex items-center gap-4">
                {isNumber(get(product, "rating")) &&
                  get(product, "rating", 0) > 0 && (
                    <div className="flex items-center gap-2">
                      <div className="flex items-center">
                        {[...Array(5)].map((_, i) => (
                          <TbStar
                            key={i}
                            className={`w-5 h-5 ${
                              i < Math.floor(get(product, "rating", 0))
                                ? "text-chart-4 fill-current"
                                : "text-muted-foreground"
                            }`}
                          />
                        ))}
                      </div>
                      <span className="font-semibold text-lg text-foreground">
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
            <div className="flex items-center gap-3">
              <TbPackage className="w-5 h-5" />
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
                className="px-3 py-1"
              >
                {get(product, "availability_status") === "Out of Stock" ||
                get(product, "stock", 0) === 0
                  ? "Out of Stock"
                  : `${get(product, "stock", 0)} in stock`}
              </Badge>
            </div>

            {/* Size Selection */}
            {size(availableSizes) > 0 && (
              <div className="space-y-3">
                <Label className="text-lg font-semibold">
                  Available Sizes:
                </Label>
                <RadioGroup
                  value={selectedSize}
                  onValueChange={setSelectedSize}
                  className="flex flex-wrap gap-2"
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
                        className={`cursor-pointer px-4 py-2 border rounded-lg transition-colors font-medium ${
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

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <Button
                className="flex-1"
                variant="outline"
                size="lg"
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
                  get(product, "stock", 0) === 0
                }
              >
                Add to Cart
              </Button>
              <Button
                className="flex-1"
                size="lg"
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
                  get(product, "stock", 0) === 0
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
          <div className="bg-card rounded-2xl p-6 shadow-sm border border-border space-y-6">
            <h2 className="text-2xl font-bold text-foreground">
              Product Details
            </h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {!isEmpty(get(product, "sku")) && (
                <div className="bg-muted rounded-xl p-4 text-center">
                  <TbBarcode className="w-8 h-8 text-primary mx-auto mb-2" />
                  <div className="text-sm text-muted-foreground mb-1">SKU</div>
                  <div className="font-semibold text-sm break-all text-foreground">
                    {get(product, "sku")}
                  </div>
                </div>
              )}

              {isNumber(get(product, "weight")) &&
                get(product, "weight", 0) > 0 && (
                  <div className="bg-muted rounded-xl p-4 text-center">
                    <TbWeight className="w-8 h-8 text-primary mx-auto mb-2" />
                    <div className="text-sm text-muted-foreground mb-1">
                      Weight
                    </div>
                    <div className="font-semibold text-foreground">
                      {get(product, "weight", 0)} lbs
                    </div>
                  </div>
                )}

              {!isEmpty(productDimensions) && (
                <div className="bg-muted rounded-xl p-4 text-center">
                  <TbRuler className="w-8 h-8 text-primary mx-auto mb-2" />
                  <div className="text-sm text-muted-foreground mb-1">
                    Dimensions
                  </div>
                  <div className="font-semibold text-xs text-foreground">
                    {get(productDimensions, "width", 0)}" ×{" "}
                    {get(productDimensions, "height", 0)}" ×{" "}
                    {get(productDimensions, "depth", 0)}"
                  </div>
                </div>
              )}

              {isNumber(get(product, "minimum_order_quantity")) &&
                get(product, "minimum_order_quantity", 1) > 1 && (
                  <div className="bg-muted rounded-xl p-4 text-center">
                    <TbPackage className="w-8 h-8 text-primary mx-auto mb-2" />
                    <div className="text-sm text-muted-foreground mb-1">
                      Minimum Order
                    </div>
                    <div className="font-semibold text-foreground">
                      {get(product, "minimum_order_quantity", 1)} units
                    </div>
                  </div>
                )}
            </div>

            {/* Tags Section */}
            {productTags.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-foreground">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {productTags
                    .slice(0, 10)
                    .map((tag: string, index: number) => (
                      <Badge
                        key={index}
                        variant="secondary"
                        className="px-3 py-1"
                      >
                        {tag}
                      </Badge>
                    ))}
                  {productTags.length > 10 && (
                    <Badge variant="outline" className="px-3 py-1">
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
            <div className="bg-card rounded-2xl p-6 shadow-sm border border-border space-y-6">
              <h2 className="text-2xl font-bold text-foreground">
                Shipping & Returns
              </h2>

              <div className="grid md:grid-cols-3 gap-4">
                {!isEmpty(get(product, "shipping_information")) && (
                  <div className="bg-chart-2/10 rounded-xl p-4 text-center border border-chart-2/20">
                    <TbTruck className="w-8 h-8 text-chart-2 mx-auto mb-3" />
                    <div className="font-semibold text-lg mb-2 text-foreground">
                      {get(product, "shipping_information").includes("1-2")
                        ? "Ships in 1-2 business days"
                        : get(product, "shipping_information")}
                    </div>
                  </div>
                )}

                {!isEmpty(get(product, "warranty_information")) && (
                  <div className="bg-chart-1/10 rounded-xl p-4 text-center border border-chart-1/20">
                    <TbShield className="w-8 h-8 text-chart-1 mx-auto mb-3" />
                    <div className="font-semibold text-lg mb-2 text-foreground">
                      {get(product, "warranty_information") === "No warranty"
                        ? "No warranty"
                        : get(product, "warranty_information")}
                    </div>
                  </div>
                )}

                {!isEmpty(get(product, "return_policy")) && (
                  <div className="bg-chart-5/10 rounded-xl p-4 text-center border border-chart-5/20">
                    <TbPackage className="w-8 h-8 text-chart-5 mx-auto mb-3" />
                    <div className="font-semibold text-lg mb-2 text-foreground">
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
