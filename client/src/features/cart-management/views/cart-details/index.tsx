import { useEffect, type FC } from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type {
  CartDetails as CartDetailsType,
  CartItemWithProductDetails,
} from "../../types";
import { get, isEmpty } from "lodash";
import { Button } from "@/components/ui/button";
import { Trash } from "lucide-react";
import { useChatStore } from "@/store/chat-store";
import { TbShoppingCartExclamation } from "react-icons/tb";
import { toast } from "sonner";

type CartDetailsProps = {
  details: CartDetailsType;
};

const CartDetails: FC<CartDetailsProps> = ({ details }) => {
  const { sendMessage } = useChatStore();

  const handleDeleteFromCart = async (item: CartItemWithProductDetails) => {
    const productDetails =
      item.product_details as CartItemWithProductDetails["product_details"];
    const productName = productDetails.title || "Unknown Product";
    const message = `I would like to delete the item ${productName} by ${item.product_details.brand} from my cart`;
    await sendMessage(message);
  };

  const handleCheckout = async () => {
    const message = `I would like to checkout`;
    await sendMessage(message);
  };

  const cartDetails = get(details, "cart_items", []);

  useEffect(() => {
    if (get(details, "message.type", "") === "success") {
      toast.success(get(details, "message.text", ""), {
        duration: 3000,
        position: "top-center",
      });
    }
  }, [details]);

  return (
    <div>
      <Card className="py-0 gap-4">
        <CardHeader className="p-4 sm:p-6">
          <CardTitle className="text-lg sm:text-xl">Cart Details</CardTitle>
        </CardHeader>
        {isEmpty(cartDetails) && (
          <CardContent className="flex flex-col items-center justify-center gap-3 sm:gap-4 py-8 sm:py-12">
            <TbShoppingCartExclamation className="w-16 h-16 sm:w-20 sm:h-20 text-neutral-600" />
            <p className="text-xs sm:text-sm font-light text-muted-foreground">
              Your cart is currently empty.
            </p>
          </CardContent>
        )}
        {!isEmpty(cartDetails) && (
          <CardContent className="p-3 sm:p-6">
            <div className="flex flex-col gap-4 sm:gap-6">
              <div className="flex flex-col gap-3 sm:gap-4">
                {cartDetails.map((item) => {
                  // Handle both old and new image structure
                  let thumbnailSrc = "";
                  const imagesData = get(item, "product_details.images", "");

                  if (typeof imagesData === "string" && imagesData) {
                    try {
                      const parsedImages = JSON.parse(imagesData);
                      // Check if it's an array (new structure) or object (old structure)
                      if (Array.isArray(parsedImages)) {
                        thumbnailSrc = parsedImages[0] || "";
                      } else {
                        thumbnailSrc = parsedImages.thumbnail || "";
                      }
                    } catch {
                      thumbnailSrc = "";
                    }
                  }

                  // Fallback to thumbnail field
                  if (!thumbnailSrc) {
                    thumbnailSrc = get(item, "product_details.thumbnail", "");
                  }

                  const productName =
                    get(item, "product_details.title", "") ||
                    get(item, "product_details.name", "");
                  const productPrice =
                    get(item, "product_details.price", "") ||
                    get(item, "unit_price", "");

                  return (
                    <div
                      key={get(item, "id", "")}
                      className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 p-3 sm:p-4 border rounded-lg hover:bg-gray-50/50 transition-colors"
                    >
                      <div className="flex gap-2.5 sm:gap-3 items-start sm:flex-1">
                        <img
                          src={thumbnailSrc}
                          alt={productName}
                          className="w-16 h-16 sm:w-20 sm:h-20 rounded-md object-cover shrink-0"
                        />
                        <div className="flex flex-col gap-1.5 sm:gap-2 flex-1 min-w-0">
                          <div>
                            <p className="text-sm sm:text-base font-semibold line-clamp-2 leading-tight">
                              {productName}
                            </p>
                            <p className="text-xs sm:text-sm text-muted-foreground mt-0.5">
                              {get(item, "product_details.brand", "")}
                            </p>
                          </div>

                          {/* Additional product details */}
                          <div className="flex gap-1.5 text-[10px] sm:text-xs text-muted-foreground flex-wrap">
                            {get(item, "size") && (
                              <span className="bg-gray-100 px-1.5 py-0.5 sm:px-2 sm:py-1 rounded">
                                Size: {get(item, "size")}
                              </span>
                            )}
                            <span className="bg-gray-100 px-1.5 py-0.5 sm:px-2 sm:py-1 rounded">
                              {get(item, "unit", "piece")}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center justify-between sm:justify-end gap-3 sm:gap-4 pl-[4.5rem] sm:pl-0">
                        <div className="flex gap-0.5 sm:gap-1 flex-col items-start sm:items-end">
                          <p className="text-xs sm:text-sm font-medium text-muted-foreground">
                            ${productPrice} × {get(item, "quantity", "")}
                          </p>
                          <p className="text-base sm:text-lg font-bold text-green-600">
                            ${get(item, "total_price", "")}
                          </p>
                        </div>

                        <Button
                          variant="ghost"
                          size="icon"
                          className="bg-destructive/10 hover:bg-destructive/20 text-destructive hover:text-destructive active:scale-95 transition-all duration-100 h-8 w-8 sm:h-9 sm:w-9"
                          onClick={() => {
                            handleDeleteFromCart(item);
                          }}
                        >
                          <Trash className="size-3.5 sm:size-4" />
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>

              <hr className="mt-2 sm:mt-4 mb-3 sm:mb-4 border-t" />

              <div className="flex flex-col gap-1.5 sm:gap-2">
                <div className="flex justify-between items-center">
                  <p className="text-xs sm:text-sm font-light text-muted-foreground">
                    Subtotal
                  </p>
                  <p className="text-sm sm:text-base font-medium">
                    ${get(details, "cart_summary.total_value", "")}
                  </p>
                </div>
                <div className="flex justify-between items-center">
                  <p className="text-xs sm:text-sm font-light text-muted-foreground">
                    Shipping
                  </p>
                  <p className="text-sm sm:text-base font-medium">
                    ${get(details, "cart_summary.shipping", "0")}
                  </p>
                </div>
                <div className="flex justify-between items-center">
                  <p className="text-xs sm:text-sm font-light text-muted-foreground">
                    Tax
                  </p>
                  <p className="text-sm sm:text-base font-medium">
                    ${get(details, "cart_summary.tax", "0")}
                  </p>
                </div>
                <div className="flex justify-between items-center mt-2 sm:mt-3 pt-2 sm:pt-3 border-t">
                  <p className="text-sm sm:text-base font-semibold">Total</p>
                  <p className="text-lg sm:text-xl font-bold">
                    ${get(details, "cart_summary.total_value", "")}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        )}
        {!isEmpty(cartDetails) && (
          <CardFooter className="flex flex-col sm:flex-row gap-4 justify-end items-end sm:gap-4 p-3 sm:p-6">
            <Button
              variant="outline"
              className="flex-1 text-sm w-full"
              onClick={async () => await sendMessage("Show me more products")}
            >
              Continue Shopping
            </Button>
            <Button
              variant="default"
              className="flex-1 text-sm w-full"
              onClick={() => {
                handleCheckout();
              }}
            >
              Checkout
            </Button>
          </CardFooter>
        )}
      </Card>
    </div>
  );
};

export default CartDetails;
