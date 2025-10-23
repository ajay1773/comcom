import { useRef, useEffect, useState } from "react";
import { LuCircleX, LuEllipsis, LuMenu } from "react-icons/lu";
import AutoResizeInput from "../auto-resize-input";
import { useChatStore } from "../../store/chat-store";
import UserMessage from "../user-message";
import AssistantMessage from "../assistant-message";
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
import BundleResults from "@/features/product-bundle-search/views/bundle-results";
import StatusCard from "../status-card";
import { get } from "lodash";
import { RateLimitSnackbar } from "../rate-limit-snackbar";
import { SidebarDesktop, SidebarMobile } from "../sidebar";
import { useMediaQuery } from "@/hooks/use-media-query";

const MoreOptionsDropdown = () => {
  const { setWidgetJson, logout } = useChatStore();

  const handleLogin = () => {
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

// Helper function to get icon component for StatusCard
const getStatusCardIcon = (iconName: string) => {
  const iconMap: Record<string, React.ReactNode> = {
    "search-x": <LuCircleX className="h-8 w-8 text-red-500" />,
    "package-plus": <LuCircleX className="h-8 w-8 text-blue-500" />,
    "alert-triangle": <LuEllipsis className="h-8 w-8 text-yellow-500" />,
  };
  return iconMap[iconName] || <LuCircleX className="h-8 w-8 text-gray-500" />;
};

// Helper function to handle StatusCard actions
const handleStatusCardAction = (action: string) => {
  console.log("StatusCard action:", action);
};

const SignedInChatWindow = () => {
  const {
    messages,
    error,
    sendMessage,
    widgetJson,
    currentStreamingMessageId,
    currentConversation,
    rateLimitStatus,
    checkRateLimitStatus,
    isLoading,
  } = useChatStore();

  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);
  const chatWindowRef = useRef<HTMLDivElement>(null);
  const lastMessageRef = useRef<HTMLDivElement>(null);
  const isDesktop = useMediaQuery("(min-width: 1024px)");

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

  useEffect(() => {
    if (currentStreamingMessageId) {
      const streamingMessage = messages.find(
        (msg) => msg.id === currentStreamingMessageId
      );
      if (streamingMessage?.content) {
        requestAnimationFrame(() => scrollToBottom());
      }
    }
  }, [currentStreamingMessageId, messages]);

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
      case "order_details":
        return <div>Order Details: {JSON.stringify(payload)}</div>;
      case "initiate_payment":
        return <PaymentForm details={payload as PaymentDetailsType} />;
      case "payment_status_details":
        return <PaymentStatus details={payload as PaymentStatusDetailsType} />;
      case "signin_form":
        return <SigninForm onSubmit={() => {}} />;
      case "signup_form":
        return <SignupForm onSubmit={() => {}} />;
      case "signup_success":
        return <SigninForm onSubmit={() => {}} />;
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
    <div className="w-full h-screen flex">
      {/* Mobile Sidebar */}
      <SidebarMobile
        open={isMobileSidebarOpen}
        onOpenChange={setIsMobileSidebarOpen}
      />

      {/* Desktop Sidebar */}
      {isDesktop && <SidebarDesktop />}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header - Always full width */}
        <div className="flex justify-between w-full px-4 sm:px-6 md:px-8 border-b border-b-neutral-400/10 h-[56px] sm:h-[64px] md:h-[68px] items-center">
          {!isDesktop && (
            <button
              onClick={() => setIsMobileSidebarOpen(true)}
              className="flex justify-center items-center hover:bg-neutral-600/10 rounded-lg p-1.5 sm:p-2 active:scale-95 transition-all duration-300 cursor-pointer group"
            >
              <LuMenu className="size-6" />
            </button>
          )}
          <h2 className="text-white text-lg sm:text-xl md:text-2xl font-semibold truncate flex-1">
            {currentConversation?.title || "New Chat"}
          </h2>
          <div className="flex justify-center items-center gap-3 sm:gap-4 md:gap-6">
            <MoreOptionsDropdown />
          </div>
        </div>

        {/* Content Area - Chat + Widget */}
        <div
          className={`flex-1 flex overflow-hidden ${
            widgetJson ? "justify-start" : "justify-center"
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
                <div className="flex flex-col items-center justify-center h-full">
                  <p className="text-neutral-500 text-base sm:text-lg font-medium mb-2">
                    Start a conversation
                  </p>
                  <p className="text-neutral-700 text-xs sm:text-sm">
                    Send a message to begin chatting with AI
                  </p>
                </div>
              ) : (
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
                      const widgetData = message.json
                        ? message.json
                        : {
                            template: get(
                              message,
                              "widget_json.widget_type",
                              ""
                            ),
                            payload: get(message, "widget_json.payload", {}),
                          };
                      const widgetComponent = getMappedTemplate(widgetData);

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
            <div className="hidden lg:flex flex-col w-2/5 h-full overflow-y-auto p-6">
              {getMappedTemplate(widgetJson)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SignedInChatWindow;
