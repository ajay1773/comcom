import StatusCard from "@/components/status-card";
import { CheckCircleIcon } from "lucide-react";
import type { AddToCartSuccess as AddToCartSuccessType } from "@/features/cart-management/types";
import type { FC } from "react";
import { Button } from "@/components/ui/button";
import { useChatStore } from "@/store/chat-store";

const AddToCartSuccess: FC<{ details: AddToCartSuccessType }> = ({
  details,
}) => {
  const { sendMessage } = useChatStore();

  return (
    <div>
      <StatusCard
        title="Added to Cart!"
        subtitle={
          details?.message
            ? String(details.message)
            : "Product has been successfully added to your cart."
        }
        icon={<CheckCircleIcon className="w-10 h-10 text-green-600" />}
        actions={
          <div className="flex gap-2 w-full">
            <Button
              variant="outline"
              className="w-1/2"
              onClick={async () => await sendMessage("Show me more products")}
            >
              Continue Shopping
            </Button>
            <Button
              className="bg-blue-500 text-white px-4 py-2 rounded-md w-1/2 hover:bg-blue-600 hover:cursor-pointer transition-all duration-300 active:bg-blue-700"
              onClick={async () => await sendMessage("Show me my cart")}
            >
              View Cart
            </Button>
          </div>
        }
      />
    </div>
  );
};

export default AddToCartSuccess;
