import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useChatStore } from "@/store/chat-store";
import {
  LuShoppingCart,
  LuStar,
  LuSparkles,
  LuCheck,
  LuInfo,
  LuPackage,
} from "react-icons/lu";
import { useState } from "react";

interface BundleProduct {
  id: number;
  title: string;
  brand: string;
  price: number;
  rating: number;
  thumbnail: string;
  priority: number;
  purpose: string;
  quantity: number;
}

interface BundleResultsProps {
  payload: {
    bundle_title: string;
    bundle_description: string;
    essential_items: Record<string, BundleProduct[]>;
    recommended_items: Record<string, BundleProduct[]>;
    optional_items: Record<string, BundleProduct[]>;
  };
}

const BundleResults = ({ payload }: BundleResultsProps) => {
  const { sendMessage } = useChatStore();
  const [addingToCart, setAddingToCart] = useState<number | null>(null);

  const handleAddToCart = async (product: BundleProduct) => {
    setAddingToCart(product.id);
    sendMessage(`Add ${product.title} to my cart`);

    // Reset after animation
    setTimeout(() => {
      setAddingToCart(null);
    }, 1500);
  };

  // Calculate total items and price
  const getTotalStats = () => {
    const allProducts = [
      ...Object.values(payload.essential_items).flat(),
      ...Object.values(payload.recommended_items).flat(),
      ...Object.values(payload.optional_items).flat(),
    ];

    const totalPrice = allProducts.reduce(
      (sum, p) => sum + p.price * p.quantity,
      0
    );
    const totalItems = allProducts.length;

    return { totalPrice, totalItems };
  };

  const { totalPrice, totalItems } = getTotalStats();

  const getPriorityIcon = (title: string) => {
    switch (title) {
      case "Essential Items":
        return <LuCheck className="w-4 h-4 sm:w-5 sm:h-5" />;
      case "Recommended Items":
        return <LuSparkles className="w-4 h-4 sm:w-5 sm:h-5" />;
      case "Optional Upgrades":
        return <LuPackage className="w-4 h-4 sm:w-5 sm:h-5" />;
      default:
        return null;
    }
  };

  const getPriorityDescription = (title: string) => {
    switch (title) {
      case "Essential Items":
        return "Must-have items to get started";
      case "Recommended Items":
        return "Highly suggested for better experience";
      case "Optional Upgrades":
        return "Nice-to-have additions";
      default:
        return "";
    }
  };

  const renderProductGroup = (
    title: string,
    items: Record<string, BundleProduct[]>,
    priorityColor: string,
    borderColor: string
  ) => {
    if (Object.keys(items).length === 0) return null;

    return (
      <div className="mb-6 sm:mb-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        {/* Priority Header */}
        <div
          className={`flex flex-col sm:flex-row items-start sm:items-center gap-2 sm:gap-3 mb-3 sm:mb-4 pb-2 sm:pb-3 border-b-2 ${borderColor}`}
        >
          <Badge
            className={`${priorityColor} text-white flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1 sm:py-1.5 text-xs sm:text-sm`}
          >
            {getPriorityIcon(title)}
            <span className="font-semibold">{title}</span>
          </Badge>
          <p className="text-xs sm:text-sm text-muted-foreground">
            {getPriorityDescription(title)}
          </p>
        </div>

        {/* Categories */}
        {Object.entries(items).map(([category, products], idx) => (
          <Card
            key={category}
            className="mb-4 sm:mb-6 overflow-hidden border-2 hover:shadow-lg transition-all duration-300"
            style={{ animationDelay: `${idx * 100}ms` }}
          >
            <CardHeader className="bg-gradient-to-r from-muted/30 to-muted/10 p-3 sm:p-6">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0">
                <div className="w-full sm:w-auto">
                  <CardTitle className="text-base sm:text-lg font-bold capitalize">
                    {category}
                  </CardTitle>
                  {products[0]?.purpose && (
                    <p className="text-xs sm:text-sm text-muted-foreground mt-1 flex items-center gap-1">
                      <LuInfo className="w-3 h-3 sm:w-4 sm:h-4" />
                      {products[0].purpose}
                    </p>
                  )}
                </div>
                <Badge
                  variant="outline"
                  className="text-[10px] sm:text-xs shrink-0"
                >
                  {products.length}{" "}
                  {products.length === 1 ? "option" : "options"}
                </Badge>
              </div>
            </CardHeader>

            <CardContent className="pt-4 sm:pt-6 p-3 sm:p-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                {products.map((product, productIdx) => (
                  <div
                    key={product.id}
                    className="group relative border-2 rounded-xl p-3 sm:p-4 hover:border-primary hover:shadow-md transition-all duration-300 bg-card flex flex-col"
                    style={{
                      animationDelay: `${idx * 100 + productIdx * 50}ms`,
                    }}
                  >
                    {/* Product Image */}
                    <div className="relative overflow-hidden rounded-lg mb-2 sm:mb-3">
                      <img
                        src={product.thumbnail}
                        alt={product.title}
                        className="w-full h-32 sm:h-36 md:h-40 object-cover transition-transform duration-300 group-hover:scale-110"
                      />
                      {product.rating >= 4.5 && (
                        <Badge className="absolute top-1.5 sm:top-2 right-1.5 sm:right-2 bg-yellow-500 text-black text-[10px] sm:text-xs">
                          <LuStar className="w-2.5 h-2.5 sm:w-3 sm:h-3 mr-0.5 sm:mr-1 fill-current" />
                          Top Rated
                        </Badge>
                      )}
                    </div>

                    {/* Product Info - grows to fill space */}
                    <div className="flex flex-col flex-1 space-y-1.5 sm:space-y-2">
                      <h4 className="font-semibold text-xs sm:text-sm line-clamp-2 min-h-[32px] sm:min-h-[40px] group-hover:text-primary transition-colors leading-tight">
                        {product.title}
                      </h4>

                      <p className="text-[10px] sm:text-xs text-muted-foreground font-medium">
                        {product.brand}
                      </p>

                      {/* Price and Rating */}
                      <div className="flex justify-between items-center pt-1 sm:pt-2">
                        <span className="text-base sm:text-lg font-bold text-primary">
                          ${product.price.toFixed(2)}
                        </span>
                        <div className="flex items-center gap-0.5 sm:gap-1 text-xs">
                          <LuStar className="w-3 h-3 sm:w-4 sm:h-4 fill-yellow-400 text-yellow-400" />
                          <span className="font-semibold">
                            {product.rating.toFixed(1)}
                          </span>
                        </div>
                      </div>

                      {/* Quantity Badge - Fixed Height */}
                      <div className="min-h-[20px] sm:min-h-[24px] flex items-center">
                        {product.quantity > 1 && (
                          <Badge
                            variant="secondary"
                            className="text-[10px] sm:text-xs"
                          >
                            Qty: {product.quantity}
                          </Badge>
                        )}
                      </div>

                      {/* Add to Cart Button - Always at bottom */}
                      <Button
                        size="sm"
                        className="w-full mt-auto group/btn relative overflow-hidden text-xs sm:text-sm h-8 sm:h-9"
                        onClick={() => handleAddToCart(product)}
                        disabled={addingToCart === product.id}
                      >
                        {addingToCart === product.id ? (
                          <>
                            <LuCheck className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2 animate-bounce" />
                            Added!
                          </>
                        ) : (
                          <>
                            <LuShoppingCart className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2 transition-transform group-hover/btn:scale-110" />
                            Add to Cart
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-3 sm:p-4 md:p-6">
      {/* Header Section */}
      <div className="mb-6 sm:mb-8 pb-4 sm:pb-6 border-b-2 animate-in fade-in slide-in-from-top-4 duration-700">
        <div className="flex items-start justify-between mb-3 sm:mb-4">
          <div className="flex-1">
            <h2 className="text-xl sm:text-2xl md:text-3xl font-bold mb-2 sm:mb-3 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent leading-tight">
              {payload.bundle_title}
            </h2>
            <p className="text-muted-foreground text-sm sm:text-base md:text-lg">
              {payload.bundle_description}
            </p>
          </div>
        </div>

        {/* Bundle Stats */}
        <div className="grid grid-cols-3 gap-2 sm:gap-3 md:gap-4 mt-4 sm:mt-6">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900 border-blue-200 dark:border-blue-800">
            <CardContent className="p-2 sm:p-3 md:p-4">
              <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-3">
                <div className="p-1.5 sm:p-2 bg-blue-500 rounded-lg shrink-0">
                  <LuPackage className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
                <div className="text-center sm:text-left">
                  <p className="text-lg sm:text-xl md:text-2xl font-bold">
                    {totalItems}
                  </p>
                  <p className="text-[10px] sm:text-xs text-muted-foreground">
                    Total Products
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900 border-green-200 dark:border-green-800">
            <CardContent className="p-2 sm:p-3 md:p-4">
              <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-3">
                <div className="p-1.5 sm:p-2 bg-green-500 rounded-lg shrink-0">
                  <LuShoppingCart className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
                <div className="text-center sm:text-left">
                  <p className="text-lg sm:text-xl md:text-2xl font-bold">
                    ${totalPrice.toFixed(2)}
                  </p>
                  <p className="text-[10px] sm:text-xs text-muted-foreground">
                    Bundle Total
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900 border-purple-200 dark:border-purple-800">
            <CardContent className="p-2 sm:p-3 md:p-4">
              <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-3">
                <div className="p-1.5 sm:p-2 bg-purple-500 rounded-lg shrink-0">
                  <LuSparkles className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                </div>
                <div className="text-center sm:text-left">
                  <p className="text-lg sm:text-xl md:text-2xl font-bold">
                    {Object.keys(payload.essential_items).length +
                      Object.keys(payload.recommended_items).length +
                      Object.keys(payload.optional_items).length}
                  </p>
                  <p className="text-[10px] sm:text-xs text-muted-foreground">
                    Categories
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Product Groups */}
      {renderProductGroup(
        "Essential Items",
        payload.essential_items,
        "bg-red-500",
        "border-red-500"
      )}
      {renderProductGroup(
        "Recommended Items",
        payload.recommended_items,
        "bg-blue-500",
        "border-blue-500"
      )}
      {renderProductGroup(
        "Optional Upgrades",
        payload.optional_items,
        "bg-gray-500",
        "border-gray-500"
      )}

      {/* Footer CTA */}
      <div className="mt-6 sm:mt-8 p-4 sm:p-6 bg-gradient-to-r from-primary/10 to-primary/5 rounded-xl border-2 border-primary/20 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-4">
          <div className="flex-1">
            <h3 className="text-base sm:text-lg font-bold mb-1">
              Ready to get started?
            </h3>
            <p className="text-xs sm:text-sm text-muted-foreground">
              Add items to your cart and complete your bundle
            </p>
          </div>
          <Button
            size="default"
            className="group w-full sm:w-auto shrink-0"
            onClick={() => sendMessage("Show me my cart")}
          >
            <LuShoppingCart className="w-4 h-4 sm:w-5 sm:h-5 mr-2 group-hover:animate-bounce" />
            View Cart
          </Button>
        </div>
      </div>
    </div>
  );
};

export default BundleResults;
