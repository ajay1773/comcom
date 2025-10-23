import { useRef, useEffect } from "react";
import AutoResizeInput from "../auto-resize-input";
import { useChatStore } from "../../store/chat-store";
import UserMessage from "../user-message";
import AssistantMessage from "../assistant-message";
import ChatHeader from "../chat-header";
import PaymentForm from "@/features/place-order/views/payment-form";
import PaymentStatus from "@/features/place-order/views/payment-status";
import type { PaymentDetails as PaymentDetailsType } from "@/features/place-order/types";
import type { PaymentStatusDetails as PaymentStatusDetailsType } from "@/features/place-order/types";
import SigninFormChat from "@/features/signin/views/signin-form-chat";
import SignupFormChat from "@/features/signup/views/signup-form-chat";
import type { SigninSuccess as SigninSuccessType } from "@/features/signin/types";
import SigninSuccess from "@/features/signin/views/signin-success";
import AddToCartSuccess from "@/features/cart-management/views/add-to-cart-success";
import type { AddToCartSuccess as AddToCartSuccessType } from "@/features/cart-management/types";
import ProductWindow, {
  type ProductWindowProps,
} from "@/features/product-search/views/product-window";
import CartDetails from "@/features/cart-management/views/cart-details";
import type { CartDetails as CartDetailsType } from "@/features/cart-management/types";
import UserProfile from "@/features/user-management/views/user-profile";
import type {
  UserAddress,
  UserProfileData,
} from "@/features/user-management/types";
import UserAddressesWindow from "@/features/user-management/views/user-addresses-window";
import CheckoutForm from "@/features/cart-management/views/checkout-form";
import type { CheckoutUIProviderData } from "@/features/cart-management/types";
import OrdersWindow, {
  type OrdersWindowProps,
} from "@/features/cart-management/views/orders-window";
import ProductsComparison from "@/features/product-comparison/views/products-comparison";
import type { ProductComparisonPayload } from "@/features/product-comparison/types";
import BundleResults from "@/features/product-bundle-search/views/bundle-results";
import StatusCard from "../status-card";
import { get } from "lodash";
import {
  LuCircleX as LuCircleXIcon,
  LuBookmark,
  LuEllipsis,
} from "react-icons/lu";
import { RateLimitSnackbar } from "../rate-limit-snackbar";

// Helper function to get icon component for StatusCard
const getStatusCardIcon = (iconName: string) => {
  const iconMap: Record<string, React.ReactNode> = {
    "search-x": <LuCircleXIcon className="h-8 w-8 text-red-500" />,
    "package-plus": <LuBookmark className="h-8 w-8 text-blue-500" />,
    "alert-triangle": <LuEllipsis className="h-8 w-8 text-yellow-500" />,
  };
  return (
    iconMap[iconName] || <LuCircleXIcon className="h-8 w-8 text-gray-500" />
  );
};

// Helper function to handle StatusCard actions
const handleStatusCardAction = (action: string) => {
  console.log("StatusCard action:", action);
};

const SignedOutChatWindow = () => {
  const {
    messages,
    error,
    sendMessage,
    widgetJson,
    currentStreamingMessageId,
    isLoading,
    rateLimitStatus,
    checkRateLimitStatus,
  } = useChatStore();

  const chatWindowRef = useRef<HTMLDivElement>(null);
  const lastMessageRef = useRef<HTMLDivElement>(null);

  // Quick action cards
  const quickActions = [
    {
      icon: "🏏",
      title: "Cricket Starter Bundle",
      subtitle: "Get everything for cricket",
      prompt: "I want to start playing cricket, what do I need?",
    },
    {
      icon: "🍳",
      title: "Kitchen Starter Kit",
      subtitle: "All essentials for your kitchen",
      prompt: "I need to set up a kitchen, what essentials do I need?",
    },
    {
      icon: "🔍",
      title: "Search Casual Shoes",
      subtitle: "Find casual shoes for men",
      prompt: "Show me casual shoes for men",
    },
    {
      icon: "⚖️",
      title: "Compare iPhone 13 vs Samsung Galaxy S10",
      subtitle: "Which one should I buy?",
      prompt: "Compare iPhone 13 vs Samsung Galaxy S10",
    },
    {
      icon: "👤",
      title: "View My Profile",
      subtitle: "Check your account info",
      prompt: "Show me my profile",
    },
    {
      icon: "🛒",
      title: "View My Cart",
      subtitle: "See your shopping cart",
      prompt: "Show me my cart",
    },
  ];

  // Auto-scroll functions
  const scrollToBottom = (behavior: ScrollBehavior = "smooth") => {
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

  useEffect(() => {
    scrollToBottom();
  }, [messages.length]);

  useEffect(() => {
    if (currentStreamingMessageId) {
      const timeoutId = setTimeout(() => scrollToBottom(), 50);
      return () => clearTimeout(timeoutId);
    }
  }, [currentStreamingMessageId, messages]);

  // Check rate limit status on component mount
  useEffect(() => {
    checkRateLimitStatus();
  }, [checkRateLimitStatus]);

  const handleMessageSubmit = async (message: string) => {
    scrollToBottom("instant");
    await sendMessage(message);
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
        return (
          <ProductWindow payload={payload as ProductWindowProps["payload"]} />
        );
      case "product_bundle_results":
        return (
          <BundleResults
            payload={
              payload as {
                bundle_title: string;
                bundle_description: string;
                essential_items: Record<
                  string,
                  Array<{
                    id: number;
                    title: string;
                    brand: string;
                    price: number;
                    rating: number;
                    thumbnail: string;
                    priority: number;
                    purpose: string;
                    quantity: number;
                  }>
                >;
                recommended_items: Record<
                  string,
                  Array<{
                    id: number;
                    title: string;
                    brand: string;
                    price: number;
                    rating: number;
                    thumbnail: string;
                    priority: number;
                    purpose: string;
                    quantity: number;
                  }>
                >;
                optional_items: Record<
                  string,
                  Array<{
                    id: number;
                    title: string;
                    brand: string;
                    price: number;
                    rating: number;
                    thumbnail: string;
                    priority: number;
                    purpose: string;
                    quantity: number;
                  }>
                >;
              }
            }
          />
        );
      case "order_details":
        return <div>Order Details: {JSON.stringify(payload)}</div>;
      case "initiate_payment":
        return <PaymentForm details={payload as PaymentDetailsType} />;
      case "payment_status_details":
        return <PaymentStatus details={payload as PaymentStatusDetailsType} />;
      case "signin_form":
        return <SigninFormChat />;
      case "signup_form":
        return <SignupFormChat />;
      case "signup_success":
        return <SigninFormChat />;
      case "signin_success":
        return <SigninSuccess details={payload as SigninSuccessType} />;
      case "add_to_cart_success":
        return <AddToCartSuccess details={payload as AddToCartSuccessType} />;
      case "cart_details":
      case "delete_from_cart_success":
      case "view_cart_success":
        return <CartDetails details={payload as CartDetailsType} />;
      case "user_profile_details":
        return <UserProfile data={payload as UserProfileData} />;
      case "user_addresses_fetch_success":
      case "delete_address_success":
      case "add_address_success":
      case "edit_address_success":
        return (
          <UserAddressesWindow
            data={
              payload as {
                message: { type: string; text: string };
                addresses: UserAddress[];
                suggested_actions: string[];
              }
            }
          />
        );
      case "checkout_ui_provider_data":
        return <CheckoutForm data={payload as CheckoutUIProviderData} />;
      case "order_view_success":
        return <OrdersWindow {...(payload as OrdersWindowProps)} />;
      case "product_comparison_results":
        return (
          <ProductsComparison payload={payload as ProductComparisonPayload} />
        );
      case "status_card_no_products_found":
      case "status_card_category_mismatch":
      case "status_card_comparison_error":
        return (
          <StatusCard
            icon={getStatusCardIcon(get(payload, "icon", "search-x"))}
            title={get(payload, "title", "No Products Found")}
            subtitle={get(payload, "subtitle", "No Products Found")}
            actions={
              get(payload, "actions", []).length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  {get(payload, "actions", []).map((action, index) => (
                    <button
                      key={index}
                      className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
                      onClick={() =>
                        handleStatusCardAction(get(action, "action", ""))
                      }
                    >
                      {get(action, "label", "")}
                    </button>
                  ))}
                </div>
              )
            }
          />
        );
      default:
        return <></>;
    }
  };

  return (
    <div className="w-full h-screen flex flex-col">
      {/* Header - Full Width */}
      <div className="shrink-0 w-full">
        <ChatHeader isLoggedIn={false} />
      </div>

      {/* Main Content Area */}
      <div
        className={`flex-1 flex overflow-hidden ${
          widgetJson
            ? "justify-start"
            : messages.length > 0
            ? "justify-center"
            : "justify-center"
        }`}
      >
        {/* Chat Area */}
        <div
          className={`flex flex-col ${
            widgetJson ? "w-full lg:w-3/5" : "w-full max-w-3xl"
          } h-full bg-transparent ${
            widgetJson
              ? "lg:border-r lg:border-r-neutral-400/10"
              : "border-none"
          }`}
        >
          {/* Chat Messages - Flexible height */}
          <div
            className="flex-1 overflow-y-auto px-4 sm:px-6 md:px-8 py-3 sm:py-4"
            ref={chatWindowRef}
          >
            {messages.length === 0 ? (
              // Welcome screen
              <div className="flex flex-col items-center justify-center min-h-full gap-6 sm:gap-10 md:gap-12 py-6 sm:py-10 md:py-12 px-2 sm:px-4">
                <div className="text-center space-y-2 sm:space-y-3 md:space-y-4 max-w-2xl w-full">
                  <div className="inline-block animate-bounce">
                    <span className="text-3xl sm:text-5xl md:text-6xl">👋</span>
                  </div>
                  <h1 className="text-xl sm:text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 bg-clip-text text-transparent px-2 leading-tight">
                    Welcome to COMCOM!
                  </h1>
                  <p className="text-xs sm:text-base md:text-lg text-muted-foreground/80 px-4">
                    Your AI shopping assistant is here to help. Try one of these
                    popular actions or just ask me anything!
                  </p>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-3 w-full max-w-5xl">
                  {quickActions.map((action, index) => (
                    <button
                      key={index}
                      onClick={() =>
                        !rateLimitStatus.isRateLimited &&
                        sendMessage(action.prompt)
                      }
                      disabled={rateLimitStatus.isRateLimited}
                      className="group relative bg-neutral-800/40 hover:bg-neutral-800/60 border border-neutral-700/50 rounded-lg sm:rounded-xl p-2.5 sm:p-4 md:p-5 text-left transition-all duration-200 hover:border-neutral-600/50 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:bg-neutral-800/40"
                    >
                      <div className="space-y-1.5 sm:space-y-2.5">
                        <div className="w-7 h-7 sm:w-9 sm:h-9 md:w-10 md:h-10 rounded-md sm:rounded-lg bg-neutral-700/50 flex items-center justify-center text-base sm:text-lg md:text-xl group-hover:scale-110 transition-transform">
                          {action.icon}
                        </div>
                        <div className="space-y-0.5">
                          <h3 className="font-medium text-foreground/90 text-[11px] sm:text-sm leading-tight line-clamp-2">
                            {action.title}
                          </h3>
                          <p className="text-[9px] sm:text-xs text-muted-foreground/70 leading-tight line-clamp-2">
                            {action.subtitle}
                          </p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              // Messages
              <div className="flex flex-col gap-3 sm:gap-4">
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
                        <p className="text-sm sm:text-base">
                          {message.content}
                        </p>
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
                    // Get widget component if this message has associated JSON
                    const widgetComponent =
                      message.json || message.widget_json
                        ? getMappedTemplate(
                            message.json ||
                              (message.widget_json as {
                                template: string;
                                payload: unknown;
                              })
                          )
                        : null;

                    return (
                      <div
                        key={message.id}
                        ref={isLastMessage ? lastMessageRef : null}
                        className={isStreamingMessage ? "scroll-mt-4" : ""}
                      >
                        <AssistantMessage
                          message={message}
                          widgetComponent={widgetComponent}
                        />
                      </div>
                    );
                  }
                })}
                {error && (
                  <div className="flex justify-start">
                    <div className="bg-red-500/20 border border-red-500/30 text-red-400 px-3 py-2 sm:px-4 sm:py-3 rounded-lg max-w-[90%] sm:max-w-[80%]">
                      <p className="text-xs sm:text-sm">Error: {error}</p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Input Area - Fixed at bottom */}
          <div className="shrink-0 flex flex-col w-full px-4 sm:px-6 md:px-8 pt-3 sm:pt-4 pb-4 sm:pb-6 md:pb-8 gap-2 border-t border-t-neutral-400/10">
            <RateLimitSnackbar />
            <AutoResizeInput
              placeholder={
                rateLimitStatus.isRateLimited
                  ? "Rate limit reached - please wait..."
                  : "Type your message here..."
              }
              onSubmit={handleMessageSubmit}
              onMessageChange={() => {}}
              disabled={rateLimitStatus.isRateLimited || isLoading}
            />
          </div>
        </div>

        {/* Widget Panel - Hidden on mobile/tablet, visible on desktop */}
        {widgetJson && (
          <div className="hidden lg:flex flex-col w-2/5 h-full overflow-y-auto">
            {getMappedTemplate(widgetJson)}
          </div>
        )}
      </div>
    </div>
  );
};

export default SignedOutChatWindow;
