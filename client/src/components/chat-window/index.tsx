import {
  LuBookmark,
  LuCircleX,
  LuEllipsis,
  LuSquareArrowOutUpRight,
  LuStar,
} from "react-icons/lu";
import AutoResizeInput from "../auto-resize-input";
import { useChat, useChatStore } from "../../store/chat-store";
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
import { Button } from "../ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuGroup,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuShortcut,
} from "@/components/ui/dropdown-menu";
import UserProfile from "@/features/user-management/views/user-profile";
import type {
  UserAddress,
  UserProfileData,
} from "@/features/user-management/types";
import UserAddressesWindow from "@/features/user-management/views/user-addresses-window";
import { useRef, useEffect } from "react";

const MoreOptionsDropdown = () => {
  const { setWidgetJson, logout } = useChatStore();

  const handleLogin = () => {
    console.log("handleLogin");
    setWidgetJson({
      template: "send_login_form",
      payload: {},
    });
  };

  const isLoggedIn = () => {
    return localStorage.getItem("jwt_token") !== null;
  };
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="size-8">
          <LuEllipsis className="size-[20px]" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="start">
        <DropdownMenuLabel>More Options</DropdownMenuLabel>
        <DropdownMenuGroup>
          <DropdownMenuItem>Share</DropdownMenuItem>
          <DropdownMenuItem>Report</DropdownMenuItem>
          <DropdownMenuItem className="text-red-300 hover:text-red-400 focus:text-red-400 active:text-red-400">
            Delete
          </DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem
          onClick={() => {
            if (isLoggedIn()) {
              logout();
            } else {
              handleLogin();
            }
          }}
        >
          {isLoggedIn() ? "Log out" : "Log in"}
          <DropdownMenuShortcut>⇧⌘Q</DropdownMenuShortcut>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

const ChatWindow = () => {
  const {
    messages,
    error,
    sendMessage,
    widgetJson,
    currentStreamingMessageId,
  } = useChat();
  const chatWindowRef = useRef<HTMLDivElement>(null);
  const lastMessageRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom function
  const scrollToBottom = (behavior: ScrollBehavior = "smooth") => {
    // Try to scroll to last message first, fallback to container scroll
    if (lastMessageRef.current) {
      lastMessageRef.current.scrollIntoView({
        behavior,
        block: "end",
        inline: "nearest",
      });
    } else if (chatWindowRef.current) {
      chatWindowRef.current.scrollTo({
        top: chatWindowRef.current.scrollHeight,
        behavior,
      });
    }
  };

  // Auto-scroll when messages change (new message added)
  useEffect(() => {
    scrollToBottom();
  }, [messages.length]);

  // Auto-scroll when streaming message is updated
  useEffect(() => {
    if (currentStreamingMessageId) {
      // Use a slight delay to ensure DOM has updated
      const timeoutId = setTimeout(() => {
        scrollToBottom();
      }, 50);

      return () => clearTimeout(timeoutId);
    }
  }, [currentStreamingMessageId, messages]);

  // Auto-scroll when streaming message content changes
  useEffect(() => {
    if (currentStreamingMessageId) {
      const streamingMessage = messages.find(
        (msg) => msg.id === currentStreamingMessageId
      );
      if (streamingMessage?.content) {
        // Use requestAnimationFrame for smoother scrolling during streaming
        requestAnimationFrame(() => {
          scrollToBottom();
        });
      }
    }
  }, [currentStreamingMessageId, messages]);

  const handleMessageSubmit = async (message: string) => {
    // Immediate scroll when user sends message
    scrollToBottom("instant");
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
      case "signup_success":
        return <SigninForm />;
      case "login_success":
        return <SigninSuccess details={payload as SigninSuccessType} />;
      case "add_to_cart_success":
        return <AddToCartSuccess details={payload as AddToCartSuccessType} />;
      case "cart_details":
        return <CartDetails details={payload as CartDetailsType} />;
      case "user_profile_details":
        return <UserProfile data={payload as UserProfileData} />;
      case "user_addresses":
        return (
          <UserAddressesWindow
            data={
              payload as {
                addresses: UserAddress[];
                suggested_actions: string[];
              }
            }
          />
        );
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
            <MoreOptionsDropdown />
          </div>
        </div>
        <div
          className="flex flex-col w-full flex-1 px-8 py-4 overflow-y-auto"
          ref={chatWindowRef}
        >
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
              {messages.map((message, index) => {
                const isLastMessage = index === messages.length - 1;
                const isStreamingMessage =
                  message.id === currentStreamingMessageId;

                if (message.role === "tool") {
                  return (
                    <div
                      key={message.id}
                      ref={isLastMessage ? lastMessageRef : null}
                    >
                      <p>{message.content}</p>
                    </div>
                  );
                }
                if (message.role === "user") {
                  return (
                    <div
                      key={message.id}
                      ref={isLastMessage ? lastMessageRef : null}
                      className={isStreamingMessage ? "scroll-mt-4" : ""}
                    >
                      <UserMessage message={message} />
                    </div>
                  );
                }
                if (message.role === "assistant") {
                  return (
                    <div
                      key={message.id}
                      ref={isLastMessage ? lastMessageRef : null}
                      className={isStreamingMessage ? "scroll-mt-4" : ""}
                    >
                      <AssistantMessage message={message} />
                    </div>
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
        <div className="flex items-center justify-between gap-10 border-b border-b-neutral-400/10 h-[68px]">
          <Button variant="ghost" size="icon" className="size-8 ml-8">
            <LuSquareArrowOutUpRight className="size-[20px]" />
          </Button>

          <Button variant="ghost" size="icon" className="size-8 mr-8">
            <LuCircleX className="size-[20px]" />
          </Button>

          {/* <div className="flex flex-col rounded-full size-[40px] relative">
            <img
              src={USER_IMAGE}
              alt="avatar"
              className="w-full h-full object-cover rounded-full"
            />
            <span className="size-3 z-2 flex justify-center items-center rounded-full bg-[#1b1d1e] absolute bottom-0 right-0">
              <span className="size-2 rounded-full bg-green-500" />
            </span>
          </div> */}

          {/* <button className="bg-white rounded-lg px-3 py-1 hover:bg-neutral-200 transition-all duration-300 active:bg-neutral-200 active:scale-95">
            <span className="text-black text-sm font-semibold">Share</span>
          </button> */}
        </div>

        <div className="flex flex-col w-full p-8 h-[calc(100%-68px)]">
          {widgetJson && getMappedTemplate(widgetJson)}
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;
