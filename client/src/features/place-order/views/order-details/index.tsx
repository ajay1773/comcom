import { Button } from "@/components/ui/button";
import type { OrderDetails } from "../../types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { useCallback, useState } from "react";
import { useChat } from "@/store/chat-store";
import { Separator } from "@/components/ui/separator";
import { FaCartArrowDown } from "react-icons/fa6";

type OrderDetailsProps = {
  details: OrderDetails;
};

const OrderDetails = ({ details }: OrderDetailsProps) => {
  const { sendMessage } = useChat();
  const [selectedAddressId, setSelectedAddressId] = useState(
    details.addresses[0]?.id
  );

  const handlePlaceOrder = useCallback(async () => {
    const selectedAddress = details.addresses.find(
      (addr) => addr.id === selectedAddressId
    );
    if (!selectedAddress) return;

    const message = `I would like to pay for ${
      details.selected_product.name
    } (${details.selected_product.brand}) with the following delivery details:
- Name: ${selectedAddress.name}
- Address: ${selectedAddress.street}, ${selectedAddress.city}, ${
      selectedAddress.state
    }
- Total Amount: $${Math.round(details.price_breakdown.total)}
`;

    await sendMessage(message);
  }, [sendMessage, selectedAddressId, details]);

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Order Details</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-8">
          <div className="flex w-full items-center justify-between">
            <div className="flex gap-2">
              <img
                className="rounded-lg w-12 h-12"
                src={details?.selected_product?.images?.thumbnail || ""}
                alt={details?.selected_product?.name || ""}
              />
              <div className="flex flex-col gap-1">
                <p className="text-lg font-semibold">
                  {details?.selected_product?.name}
                </p>
                <span className="flex items-center justify-baseline gap-1">
                  <p className="text-sm font-light">
                    {details.selected_product.brand}
                  </p>
                </span>
              </div>
            </div>
            <div className="flex flex-col gap-1 items-end">
              <p className="text-md font-medium">
                ${Math.round(details?.selected_product?.min_price)}
              </p>
              <p className="text-sm font-light">Quantity: 1</p>
            </div>
          </div>

          <Separator />

          <RadioGroup
            value={selectedAddressId}
            onValueChange={setSelectedAddressId}
            className="flex w-full min-h-12 gap-4"
          >
            {details?.addresses.map((address) => (
              <div
                key={address.id}
                className="flex items-center w-1/2 h-full border border-input border-dashed rounded-lg p-4 gap-4 cursor-pointer hover:border-neutral-500 transition-all duration-300"
              >
                <RadioGroupItem value={address.id} id={address.id} />
                <Label htmlFor={address.id}>
                  <div className="flex flex-col">
                    <p className="text-sm font-base mb-1">{address.name}</p>
                    <p className="text-sm font-light">{address.street}</p>
                    <p className="text-sm font-light">{address.city}</p>
                    <p className="text-sm font-light">{address.state}</p>
                  </div>
                </Label>
              </div>
            ))}
          </RadioGroup>

          <Separator />

          <div className="flex flex-col gap-1">
            <div className="flex justify-between items-center w-full">
              <p className="text-sm font-light">Tax</p>
              <p className="text-md font-medium">
                ${Math.round(details?.price_breakdown?.tax)}
              </p>
            </div>
            <div className="flex justify-between items-center w-full">
              <p className="text-sm font-light">Shipping</p>
              <p className="text-md font-medium">
                ${Math.round(details?.price_breakdown?.shipping)}
              </p>
            </div>
            <div className="flex justify-between items-center w-full">
              <p className="text-sm font-light">Subtotal</p>
              <p className="text-md font-medium">
                ${Math.round(details?.price_breakdown?.subtotal)}
              </p>
            </div>
            <Separator className="my-2" />
            <div className="flex justify-between items-center w-full">
              <p className="text-sm font-light">Total</p>
              <p className="text-xl font-semibold">
                ${Math.round(details?.price_breakdown?.total)}
              </p>
            </div>
          </div>

          <div className="flex justify-end gap-2 w-full mt-4">
            <Button
              variant="default"
              className="w-1/3"
              onClick={handlePlaceOrder}
            >
              Place Order
              <FaCartArrowDown className="size-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default OrderDetails;
