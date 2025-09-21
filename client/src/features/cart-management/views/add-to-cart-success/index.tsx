import StatusCard from "@/components/status-card";
import { CheckCircleIcon } from "lucide-react";
import type { AddToCartSuccess as AddToCartSuccessType } from "@/features/cart-management/types";
import type { FC } from "react";
import { Button } from "@/components/ui/button";
import { useChat } from "@/store/chat-store";

const AddToCartSuccess: FC<{ details: AddToCartSuccessType }> = () => {
  const { sendMessage } = useChat();

  return (
    <div>
      <StatusCard
        title="Add to Cart Success"
        subtitle="You have been successfully added to cart."
        icon={<CheckCircleIcon className="w-10 h-10 text-green-600" />}
        actions={
          <div className="flex gap-2 w-full justify-center">
            <Button
              className="bg-blue-500 text-white px-4 py-2 rounded-md w-full hover:bg-blue-600 hover:cursor-pointer transition-all duration-300 :active:bg-blue-700"
              onAbort={() => sendMessage("Show me my cart")}
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
