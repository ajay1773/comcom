import {
  LuBookmark,
  LuEllipsis,
  LuSquareArrowOutUpRight,
  LuStar,
} from "react-icons/lu";

import AutoResizeInput from "../auto-resize-input";
import { useChat } from "../../store/chat-store";
import { USER_IMAGE } from "../../config";
import UserMessage from "../user-message";
import AssistantMessage from "../assistant-message";
import PaymentForm from "@/features/place-order/views/payment-form";
import PaymentStatus from "@/features/place-order/views/payment-status";
import OrderDetails from "@/features/place-order/views/order-details";
import type { Product } from "@/features/product-search/types";
import type { OrderDetails as OrderDetailsType } from "@/features/place-order/types";
import type { PaymentDetails as PaymentDetailsType } from "@/features/place-order/types";
import type { PaymentStatusDetails as PaymentStatusDetailsType } from "@/features/place-order/types";
import SigninForm from "@/features/signin/views/signin-form";
import SignupForm from "@/features/signup/views/signup-form";
import type { SigninSuccess as SigninSuccessType } from "@/features/signin/types";
import SigninSuccess from "@/features/signin/views/signin-success";
import AddToCartSuccess from "@/features/cart-management/views/add-to-cart-success";
import type { AddToCartSuccess as AddToCartSuccessType } from "@/features/cart-management/types";
import ProductWindow from "@/features/product-search/views/product-window";
import CartDetails from "@/features/cart-management/views/cart-details";
import type { CartDetails as CartDetailsType } from "@/features/cart-management/types";

const ChatWindow = () => {
  const { messages, error, sendMessage, widgetJson } = useChat();

  const handleMessageSubmit = async (message: string) => {
    await sendMessage(message);
  };

  const handleMessageChange = (message: string) => {
    // Handle message change logic here (optional)
    console.log("Message changed:", message);
  };

  const getMappedTemplate = ({
    template,
    payload,
  }: {
    template: string;
    payload: unknown;
  }) => {
    switch (template) {
      case "product_search_results":
        return <ProductWindow products={payload as Product[]} />;
      case "order_details":
        return <OrderDetails details={payload as OrderDetailsType} />;
      case "initiate_payment":
        return <PaymentForm details={payload as PaymentDetailsType} />;
      case "payment_status_details":
        return <PaymentStatus details={payload as PaymentStatusDetailsType} />;
      case "send_login_form":
        return <SigninForm />;
      case "send_signup_form":
        return <SignupForm />;
      case "login_success":
        return <SigninSuccess details={payload as SigninSuccessType} />;
      case "add_to_cart_success":
        return <AddToCartSuccess details={payload as AddToCartSuccessType} />;
      case "cart_details":
        return <CartDetails details={payload as CartDetailsType} />;
      default:
        return <></>;
    }
  };

  return (
    <div className="w-4/5 h-full flex bg-transparent">
      <div className="flex flex-col w-3/5 h-full bg-neutral-600/10 rounded-l-2xl border-r border-r-neutral-400/10">
        <div className="flex justify-between w-full px-8 border-b border-b-neutral-400/10 h-[68px]  items-center">
          <h2 className="text-white text-2xl font-semibold">Convo with AI</h2>
          <div className="flex justify-center items-center gap-6">
            <button className="flex justify-center items-center hover:bg-neutral-600/10 rounded-lg p-2 active:scale-95 transition-all duration-300 cursor-pointer group">
              <LuStar className="text-neutral-600 size-[20px] group-hover:text-white transition-all duration-300" />
            </button>
            <button className="flex justify-center items-center hover:bg-neutral-600/10 rounded-lg p-2 active:scale-95 transition-all duration-300 cursor-pointer group">
              <LuBookmark className="text-neutral-600 size-[20px] group-hover:text-white transition-all duration-300" />
            </button>
            <button className="flex justify-center items-center hover:bg-neutral-600/10 rounded-lg p-2 active:scale-95 transition-all duration-300 cursor-pointer group">
              <LuEllipsis className="text-neutral-600 size-[20px] group-hover:text-white transition-all duration-300" />
            </button>
          </div>
        </div>
        <div className="flex flex-col w-full flex-1 px-8 py-4 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full">
              <p className="text-neutral-500 text-lg font-medium mb-2">
                Start a conversation
              </p>
              <p className="text-neutral-700 text-sm">
                Send a message to begin chatting with AI
              </p>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {messages.map((message) => {
                if (message.role === "tool") {
                  return <p>{message.content}</p>;
                }
                if (message.role === "user") {
                  return <UserMessage key={message.id} message={message} />;
                }
                if (message.role === "assistant") {
                  return (
                    <AssistantMessage key={message.id} message={message} />
                  );
                }
              })}
              {error && (
                <div className="flex justify-start">
                  <div className="bg-red-500/20 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg max-w-[80%]">
                    <p className="text-sm">Error: {error}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="flex flex-col w-full px-8 pb-8">
          <AutoResizeInput
            placeholder="Type your message here..."
            onSubmit={handleMessageSubmit}
            onMessageChange={handleMessageChange}
          />
        </div>
      </div>

      <div className="flex flex-col w-2/5 h-full bg-neutral-600/10 rounded-r-2xl">
        <div className="flex items-center justify-center gap-10 border-b border-b-neutral-400/10 h-[68px]">
          <LuSquareArrowOutUpRight className="text-neutral-600 size-[20px] ml-[52px]" />

          <div className="flex flex-col rounded-full size-[40px] relative">
            <img
              src={USER_IMAGE}
              alt="avatar"
              className="w-full h-full object-cover rounded-full"
            />
            <span className="size-3 z-2 flex justify-center items-center rounded-full bg-[#1b1d1e] absolute bottom-0 right-0">
              <span className="size-2 rounded-full bg-green-500" />
            </span>
          </div>

          <button className="bg-white rounded-lg px-3 py-1 hover:bg-neutral-200 transition-all duration-300 active:bg-neutral-200 active:scale-95">
            <span className="text-black text-sm font-semibold">Share</span>
          </button>
        </div>

        <div className="flex flex-col w-full p-8 h-[calc(100%-68px)]">
          {widgetJson && getMappedTemplate(widgetJson)}
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
