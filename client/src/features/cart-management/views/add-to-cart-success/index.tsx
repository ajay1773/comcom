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
        icon={
          <CheckCircleIcon className="w-12 h-12 sm:w-14 sm:h-14 text-green-600" />
        }
        actions={
          <div className="flex flex-col sm:flex-row gap-2 w-full">
            <Button
              variant="outline"
              className="flex-1 text-sm"
              onClick={async () => await sendMessage("Show me more products")}
            >
              Continue Shopping
            </Button>
            <Button
              className="flex-1 text-sm"
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
