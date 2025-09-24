import { type FC } from "react";
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
import { get } from "lodash";
import { Button } from "@/components/ui/button";
import { Trash } from "lucide-react";
import { useChat } from "@/store/chat-store";

type CartDetailsProps = {
  details: CartDetailsType;
};

const CartDetails: FC<CartDetailsProps> = ({ details }) => {
  const { sendMessage } = useChat();

  const handleDeleteFromCart = async (item: CartItemWithProductDetails) => {
    const message = `I would like to delete the item ${item.product_details.name} by ${item.product_details.brand} from my cart`;
    await sendMessage(message);
  };

  return (
    <div>
      <Card>
        <CardHeader>
          <CardTitle>Cart Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-6">
            <div className="flex flex-col gap-4">
              {get(details, "cart_details", []).map((item) => {
                const images = JSON.parse(
                  get(item, "product_details.images", "{}") as string
                );
                return (
                  <div key={item.id} className="flex justify-between">
                    <div className="flex gap-2 items-center">
                      <img
                        src={get(images, "thumbnail", "")}
                        alt={get(item, "product_details.name", "")}
                        className="w-12 h-12 rounded-lg"
                      />
                      <div className="flex flex-col gap-1">
                        <p className="text-lg font-semibold max-w-[240px] truncate">
                          {get(item, "product_details.name", "")}
                        </p>
                        <p className="text-sm font-light">
                          {get(item, "product_details.brand", "")}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="flex gap-1 flex-col items-end">
                        <p className="text-md font-medium">
                          ${get(item, "product_details.price", "")} x{" "}
                          {get(item, "quantity", "")}
                        </p>
                        <p className="text-sm font-light">
                          ${get(item, "total_price", "")}
                        </p>
                      </div>

                      <Button
                        variant="ghost"
                        size="icon"
                        className="bg-destructive/10 hover:bg-destructive/20 text-destructive hover:text-destructive active:scale-95 transition-all duration-100"
                        onClick={() => {
                          handleDeleteFromCart(item);
                        }}
                      >
                        <Trash className="size-4" />
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>

            <hr className="mt-4 mb-2 bg-gray-600 w-full h-[1px]" />

            <div className="flex flex-col">
              <div className="flex justify-between items-center">
                <p className="text-sm font-light">Subtotal</p>
                <p className="text-md font-medium">
                  ${get(details, "cart_summary.total_value", "")}
                </p>
              </div>
              <div className="flex justify-between items-center">
                <p className="text-sm font-light">Shipping</p>
                <p className="text-md font-medium">
                  ${get(details, "cart_summary.shipping", "0")}
                </p>
              </div>
              <div className="flex justify-between items-center">
                <p className="text-sm font-light">Tax</p>
                <p className="text-md font-medium">
                  ${get(details, "cart_summary.tax", "0")}
                </p>
              </div>
              <div className="flex justify-between items-center mt-2">
                <p className="text-md font-medium">Total</p>
                <p className="text-xl font-semibold">
                  ${get(details, "cart_summary.total_value", "")}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex gap-4">
          <Button variant="outline" className="flex-1/2">
            Continue Shopping
          </Button>
          <Button variant="default" className="flex-1/2">
            Checkout
          </Button>
        </CardFooter>
      </Card>
    </div>
  );
};

export default CartDetails;
