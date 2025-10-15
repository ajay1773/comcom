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
import SigninForm from "@/features/signin/views/signin-form";
import SignupForm from "@/features/signup/views/signup-form";
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
import StatusCard from "../status-card";
import { get } from "lodash";
import {
  LuCircleX as LuCircleXIcon,
  LuBookmark,
  LuEllipsis,
} from "react-icons/lu";

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
    setWidgetJson,
    currentStreamingMessageId,
  } = useChatStore();

  const chatWindowRef = useRef<HTMLDivElement>(null);
  const lastMessageRef = useRef<HTMLDivElement>(null);

  // Quick action cards
  const quickActions = [
    {
      icon: "🛍️",
      title: "Browse Products",
      subtitle: "Explore our collection",
    },
    {
      icon: "🔍",
      title: "Search & Compare",
      subtitle: "Find the perfect item",
    },
    {
      icon: "✨",
      title: "Get Recommendations",
      subtitle: "Personalized suggestions",
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

  const handleMessageSubmit = async (message: string) => {
    scrollToBottom("instant");
    await sendMessage(message);
  };

  const handleSignIn = () => {
    setWidgetJson({
      template: "signin_form",
      payload: {},
    });
  };

  const handleSignUp = () => {
    setWidgetJson({
      template: "signup_form",
      payload: {},
    });
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
      case "order_details":
        return <div>Order Details: {JSON.stringify(payload)}</div>;
      case "initiate_payment":
        return <PaymentForm details={payload as PaymentDetailsType} />;
      case "payment_status_details":
        return <PaymentStatus details={payload as PaymentStatusDetailsType} />;
      case "signin_form":
        return <SigninForm />;
      case "signup_form":
        return <SignupForm />;
      case "signup_success":
        return <SigninForm />;
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
              get(payload, "actions", []) && (
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
    <>
      <ChatHeader
        isLoggedIn={false}
        onSignIn={handleSignIn}
        onSignUp={handleSignUp}
      />

      <div
        className={`w-full h-screen pt-16 flex ${
          widgetJson
            ? "justify-start"
            : messages.length > 0
            ? "justify-center"
            : "justify-center items-center"
        }`}
      >
        {/* Chat Area */}
        <div
          className={`flex flex-col ${
            widgetJson ? "w-3/5" : "w-full max-w-3xl"
          } ${
            widgetJson || messages.length > 0
              ? "h-full bg-transparent"
              : "h-auto bg-transparent"
          } ${widgetJson ? "border-r border-r-neutral-400/10" : "border-none"}`}
        >
          {/* Only show header when there are messages */}
          {/* {messages.length > 0 && (
            <div className="flex justify-between w-full px-8 border-b border-b-neutral-400/10 h-[68px] items-center">
              <h2 className="text-white text-2xl font-semibold">New Chat</h2>
            </div>
          )} */}

          <div
            className="flex flex-col w-full flex-1 px-8 py-4 overflow-y-auto"
            ref={chatWindowRef}
          >
            {messages.length === 0 ? (
              // Welcome screen
              <div className="flex flex-col items-center justify-center min-h-[calc(100vh-16rem)] gap-12 py-12">
                <div className="text-center">
                  <h1 className="text-3xl font-normal text-foreground/90">
                    Ready when you are.
                  </h1>
                </div>

                <div className="grid grid-cols-3 gap-3 w-full max-w-3xl">
                  {quickActions.map((action, index) => (
                    <button
                      key={index}
                      onClick={() => sendMessage(action.title)}
                      className="group relative bg-neutral-800/40 hover:bg-neutral-800/60 border border-neutral-700/50 rounded-xl p-5 text-left transition-all duration-200 hover:border-neutral-600/50"
                    >
                      <div className="space-y-2.5">
                        <div className="w-10 h-10 rounded-lg bg-neutral-700/50 flex items-center justify-center text-xl">
                          {action.icon}
                        </div>
                        <div className="space-y-0.5">
                          <h3 className="font-medium text-foreground/90 text-sm">
                            {action.title}
                          </h3>
                          <p className="text-xs text-muted-foreground/70">
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
              onMessageChange={() => {}}
            />
          </div>
        </div>

        {/* Widget Panel - only when there's content */}
        {/* {widgetJson && (
          <div className="flex flex-col w-1/2 max-w-2xl mr-8 h-full bg-neutral-800/40 rounded-xl border border-neutral-700/50">
            <div className="flex items-center justify-between gap-10 border-b border-b-neutral-400/10 h-[68px]">
              <Button variant="ghost" size="icon" className="size-8 ml-8">
                <LuSquareArrowOutUpRight className="size-[20px]" />
              </Button>
              <Button variant="ghost" size="icon" className="size-8 mr-8">
                <LuCircleX className="size-[20px]" />
              </Button>
            </div>
          </div>
        )} */}
        {widgetJson && (
          <div className="flex flex-col w-2/5 h-full overflow-y-auto">
            {getMappedTemplate(widgetJson)}
          </div>
        )}
      </div>
    </>
  );
};

export default SignedOutChatWindow;
