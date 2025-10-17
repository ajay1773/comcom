import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useChatStore } from "@/store/chat-store";

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

  const handleAddToCart = (product: BundleProduct) => {
    sendMessage(`Add ${product.title} to my cart`);
  };

  const renderProductGroup = (
    title: string,
    items: Record<string, BundleProduct[]>,
    priorityColor: string
  ) => {
    if (Object.keys(items).length === 0) return null;

    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Badge className={priorityColor}>{title}</Badge>
        </h3>

        {Object.entries(items).map(([category, products]) => (
          <Card key={category} className="mb-4">
            <CardHeader>
              <CardTitle className="text-md">{category}</CardTitle>
              {products[0]?.purpose && (
                <p className="text-sm text-muted-foreground">
                  {products[0].purpose}
                </p>
              )}
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {products.map((product) => (
                  <div key={product.id} className="border rounded-lg p-3">
                    <img
                      src={product.thumbnail}
                      alt={product.title}
                      className="w-full h-32 object-cover rounded mb-2"
                    />
                    <h4 className="font-medium text-sm truncate">
                      {product.title}
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      {product.brand}
                    </p>
                    <div className="flex justify-between items-center mt-2">
                      <span className="font-bold">${product.price}</span>
                      <span className="text-xs">⭐ {product.rating}</span>
                    </div>
                    {product.quantity > 1 && (
                      <p className="text-xs text-blue-600">
                        Qty: {product.quantity}
                      </p>
                    )}
                    <Button
                      size="sm"
                      className="w-full mt-2"
                      onClick={() => handleAddToCart(product)}
                    >
                      Add to Cart
                    </Button>
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
    <div className="w-full max-w-6xl p-4">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">{payload.bundle_title}</h2>
        <p className="text-muted-foreground">{payload.bundle_description}</p>
      </div>

      {renderProductGroup(
        "Essential Items",
        payload.essential_items,
        "bg-red-500"
      )}
      {renderProductGroup(
        "Recommended Items",
        payload.recommended_items,
        "bg-blue-500"
      )}
      {renderProductGroup(
        "Optional Upgrades",
        payload.optional_items,
        "bg-gray-500"
      )}
    </div>
  );
};

export default BundleResults;
