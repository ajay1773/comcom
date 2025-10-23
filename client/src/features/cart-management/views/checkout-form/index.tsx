import { type FC, useCallback, useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { get, isEmpty, includes, find, toString } from "lodash";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Badge } from "@/components/ui/badge";
import type { CheckoutUIProviderData } from "@/features/cart-management/types";
import { useChatStore } from "@/store/chat-store";
import {
  LuShoppingCart,
  LuUser,
  LuMapPin,
  LuCreditCard,
  LuCheck,
  LuChevronLeft,
  LuChevronRight,
} from "react-icons/lu";

const checkoutFormSchema = z
  .object({
    // User Information
    name: z
      .string()
      .min(2, { message: "Name must be at least 2 characters." })
      .max(50, { message: "Name must not exceed 50 characters." })
      .regex(/^[a-zA-Z\s]*$/, {
        message: "Name can only contain letters and spaces.",
      }),
    email: z
      .string()
      .email({ message: "Please enter a valid email address." })
      .min(1, { message: "Email is required." }),
    phone: z
      .string()
      .min(10, { message: "Phone number must be at least 10 digits." })
      .max(15, { message: "Phone number must not exceed 15 digits." })
      .regex(/^[+]?[0-9\s\-()]*$/, {
        message: "Please enter a valid phone number.",
      }),

    // Address Selection
    selectedAddressId: z
      .string()
      .min(1, { message: "Please select a shipping address." }),

    // Payment Method
    paymentMethod: z.enum(["cash_on_delivery", "credit_card"], {
      message: "Please select a payment method.",
    }),

    // Credit Card Details (conditional - validated individually)
    cardHolderName: z.string().optional(),
    cardNumber: z.string().optional(),
    cvv: z.string().optional(),
    expiryDate: z.string().optional(),
  })
  .superRefine((data, ctx) => {
    // Only validate credit card fields when credit card payment is selected
    if (data.paymentMethod === "credit_card") {
      // Cardholder Name validation
      if (!data.cardHolderName || data.cardHolderName.length < 2) {
        ctx.addIssue({
          code: "custom",
          message: "Cardholder name must be at least 2 characters.",
          path: ["cardHolderName"],
        });
      }

      // Card Number validation
      if (
        !data.cardNumber ||
        data.cardNumber.length !== 19 ||
        !/^\d{4}\s\d{4}\s\d{4}\s\d{4}$/.test(data.cardNumber)
      ) {
        ctx.addIssue({
          code: "custom",
          message: "Please enter a valid 16-digit card number.",
          path: ["cardNumber"],
        });
      }

      // CVV validation
      if (!data.cvv || data.cvv.length !== 3 || !/^\d{3}$/.test(data.cvv)) {
        ctx.addIssue({
          code: "custom",
          message: "CVV must be 3 digits.",
          path: ["cvv"],
        });
      }

      // Expiry Date validation
      if (
        !data.expiryDate ||
        !/^(0[1-9]|1[0-2])\/\d{2}$/.test(data.expiryDate)
      ) {
        ctx.addIssue({
          code: "custom",
          message: "Please enter expiry date in MM/YY format.",
          path: ["expiryDate"],
        });
      }
    }
  });

type CheckoutFormData = z.infer<typeof checkoutFormSchema>;

type CheckoutFormProps = {
  data: CheckoutUIProviderData;
};

type Step = {
  id: number;
  name: string;
  icon: React.ReactNode;
  fields: (keyof CheckoutFormData)[];
};

const steps: Step[] = [
  {
    id: 1,
    name: "Order Summary",
    icon: <LuShoppingCart className="w-4 h-4" />,
    fields: [],
  },
  {
    id: 2,
    name: "Personal Info",
    icon: <LuUser className="w-4 h-4" />,
    fields: ["name", "email", "phone"],
  },
  {
    id: 3,
    name: "Shipping",
    icon: <LuMapPin className="w-4 h-4" />,
    fields: ["selectedAddressId"],
  },
  {
    id: 4,
    name: "Payment",
    icon: <LuCreditCard className="w-4 h-4" />,
    fields: [
      "paymentMethod",
      "cardHolderName",
      "cardNumber",
      "cvv",
      "expiryDate",
    ],
  },
];

const CheckoutForm: FC<CheckoutFormProps> = ({ data }) => {
  const { sendMessage } = useChatStore();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);

  const form = useForm<CheckoutFormData>({
    resolver: zodResolver(checkoutFormSchema),
    mode: "onChange",
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      selectedAddressId:
        get(data, "saved_addresses", [])
          .find((addr) => get(addr, "is_default", false))
          ?.id?.toString() || "",
      paymentMethod:
        (get(data, "allowed_payment_methods", [])[0] as
          | "cash_on_delivery"
          | "credit_card") || "cash_on_delivery",
      cardHolderName: "",
      cardNumber: "",
      cvv: "",
      expiryDate: "",
    },
  });

  const paymentMethod = form.watch("paymentMethod");

  const formatCardNumber = useCallback((value: string) => {
    const digits = value.replace(/\D/g, "");
    const groups = digits.match(/.{1,4}/g) || [];
    return groups.join(" ").substr(0, 19);
  }, []);

  const formatExpiryDate = useCallback((value: string) => {
    const digits = value.replace(/\D/g, "");
    if (digits.length <= 2) return digits;
    return `${digits.slice(0, 2)}/${digits.slice(2, 4)}`;
  }, []);

  const formatPhoneNumber = useCallback((value: string) => {
    const digits = value.replace(/\D/g, "");
    if (digits.length <= 3) return digits;
    if (digits.length <= 6) return `${digits.slice(0, 3)}-${digits.slice(3)}`;
    return `${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6, 10)}`;
  }, []);

  // Validate current step fields
  const validateCurrentStep = async () => {
    const currentStepFields = steps[currentStep - 1].fields;

    if (currentStepFields.length === 0) return true; // Step 1 has no fields to validate

    // Special handling for payment step
    if (currentStep === 4) {
      if (paymentMethod === "credit_card") {
        const result = await form.trigger([
          "paymentMethod",
          "cardHolderName",
          "cardNumber",
          "cvv",
          "expiryDate",
        ]);
        return result;
      } else {
        const result = await form.trigger(["paymentMethod"]);
        return result;
      }
    }

    const result = await form.trigger(currentStepFields);
    return result;
  };

  const nextStep = async () => {
    const isValid = await validateCurrentStep();
    if (isValid && currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const onSubmit = useCallback(
    async (formData: CheckoutFormData) => {
      setIsSubmitting(true);

      try {
        const savedAddresses = get(data, "saved_addresses", []);
        const selectedAddress = find(
          savedAddresses,
          (addr) =>
            toString(get(addr, "id")) === get(formData, "selectedAddressId")
        );

        const name = get(formData, "name", "");
        const email = get(formData, "email", "");
        const phone = get(formData, "phone", "");
        const selectedAddressId = get(formData, "selectedAddressId", "");
        const paymentMethod = get(formData, "paymentMethod", "");

        let message = `I want to complete my checkout with the following details:

Personal Information:
- Name: ${name}
- Email: ${email}
- Phone: ${phone}

Shipping Address: Use address ID ${selectedAddressId}`;

        if (selectedAddress) {
          const street = get(selectedAddress, "street", "");
          const city = get(selectedAddress, "city", "");
          const state = get(selectedAddress, "state", "");
          const zipCode = get(selectedAddress, "zip_code", "");
          message += ` (${street}, ${city}, ${state} ${zipCode})`;
        }

        const paymentMethodText =
          paymentMethod === "cash_on_delivery"
            ? "Cash on Delivery"
            : "Credit Card";
        message += `\n\nPayment Method: ${paymentMethodText}`;

        if (paymentMethod === "credit_card") {
          const cardHolderName = get(formData, "cardHolderName", "");
          const cardNumber = get(formData, "cardNumber", "");
          const cvv = get(formData, "cvv", "");
          const expiryDate = get(formData, "expiryDate", "");

          message += `
Credit Card Details:
- Cardholder Name: ${cardHolderName}
- Card Number: ${cardNumber}
- CVV: ${cvv}
- Expiry Date: ${expiryDate}`;
        }

        await sendMessage(message);
      } catch (error) {
        console.error("Error submitting checkout:", error);
      } finally {
        setIsSubmitting(false);
      }
    },
    [data, sendMessage]
  );

  const renderStepIndicator = () => (
    <div className="mb-6 sm:mb-8">
      {/* Desktop Stepper */}
      <div className="hidden sm:flex items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center flex-1">
            <div className="flex flex-col items-center">
              <div
                className={`flex items-center justify-center w-10 h-10 rounded-full transition-all duration-300 z-10 ${
                  currentStep > step.id
                    ? "bg-green-500 text-white"
                    : currentStep === step.id
                    ? "bg-blue-600 text-white ring-4 ring-blue-600/20"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {currentStep > step.id ? (
                  <LuCheck className="w-5 h-5" />
                ) : (
                  step.icon
                )}
              </div>
              <span
                className={`text-xs mt-2 text-center transition-colors ${
                  currentStep >= step.id
                    ? "text-foreground font-medium"
                    : "text-muted-foreground"
                }`}
              >
                {step.name}
              </span>
            </div>
            {index < steps.length - 1 && (
              <div className="flex-1 h-0.5 mx-2 -mt-5 relative">
                <div
                  className={`h-full transition-all duration-300 ${
                    currentStep > step.id ? "bg-green-500" : "bg-muted"
                  }`}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Mobile Stepper */}
      <div className="flex sm:hidden items-center justify-between">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center flex-1">
            <div className="flex flex-col items-center w-full">
              <div
                className={`flex items-center justify-center w-8 h-8 rounded-full transition-all duration-300 z-10 ${
                  currentStep > step.id
                    ? "bg-green-500 text-white"
                    : currentStep === step.id
                    ? "bg-blue-600 text-white ring-2 ring-blue-600/20"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {currentStep > step.id ? (
                  <LuCheck className="w-4 h-4" />
                ) : (
                  <div className="text-xs font-semibold">{step.id}</div>
                )}
              </div>
            </div>
            {index < steps.length - 1 && (
              <div className="flex-1 h-0.5 mx-1 -mt-4">
                <div
                  className={`h-full transition-all duration-300 ${
                    currentStep > step.id ? "bg-green-500" : "bg-muted"
                  }`}
                />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Mobile Step Title */}
      <div className="sm:hidden text-center mt-3">
        <p className="text-sm font-medium text-foreground">
          {steps[currentStep - 1].name}
        </p>
        <p className="text-xs text-muted-foreground mt-0.5">
          Step {currentStep} of {steps.length}
        </p>
      </div>
    </div>
  );

  const renderOrderSummary = () => (
    <div className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-500">
      <div className="space-y-3">
        {get(data, "product_items", []).map((item) => {
          const productId = get(item, "product_id", "");
          const size = get(item, "size", "");
          const productDetails = get(item, "product_details", {});

          let thumbnailSrc = "";
          const imagesData = get(productDetails, "images", "");

          if (typeof imagesData === "string" && imagesData) {
            try {
              const parsedImages = JSON.parse(imagesData);
              if (Array.isArray(parsedImages)) {
                thumbnailSrc = parsedImages[0] || "";
              } else {
                thumbnailSrc = parsedImages.thumbnail || "";
              }
            } catch {
              thumbnailSrc = "";
            }
          }

          if (!thumbnailSrc) {
            thumbnailSrc = get(productDetails, "thumbnail", "");
          }

          const productName =
            get(productDetails, "title", "") || get(productDetails, "name", "");
          const brandName = get(productDetails, "brand", "");
          const totalPrice = get(item, "total_price", 0);
          const quantity = get(item, "quantity", 0);
          const unitPrice =
            get(productDetails, "price", 0) || get(item, "unit_price", 0);

          return (
            <div
              key={`${productId}-${size}`}
              className="flex flex-col sm:flex-row gap-3 p-3 sm:p-4 bg-muted/30 rounded-lg border border-border hover:border-primary/50 transition-colors"
            >
              <img
                src={thumbnailSrc}
                alt={productName}
                className="w-full h-48 sm:w-20 sm:h-20 object-cover rounded-md flex-shrink-0"
              />
              <div className="flex flex-col gap-1.5 flex-1 min-w-0">
                <div>
                  <h4 className="font-semibold text-sm sm:text-base line-clamp-2">
                    {productName}
                  </h4>
                  <p className="text-xs text-muted-foreground">{brandName}</p>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  {!isEmpty(size) && (
                    <Badge
                      variant="secondary"
                      className="text-[10px] sm:text-xs"
                    >
                      Size: {size}
                    </Badge>
                  )}
                  <Badge variant="outline" className="text-[10px] sm:text-xs">
                    ${unitPrice.toFixed(2)} each
                  </Badge>
                  <Badge variant="outline" className="text-[10px] sm:text-xs">
                    Qty: {quantity}
                  </Badge>
                </div>
              </div>
              <div className="flex items-center justify-between sm:justify-end sm:flex-col sm:items-end border-t sm:border-t-0 pt-3 sm:pt-0">
                <span className="text-xs sm:hidden text-muted-foreground">
                  Total:
                </span>
                <p className="text-lg sm:text-lg font-bold whitespace-nowrap">
                  ${totalPrice.toFixed(2)}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex items-center justify-between p-3 sm:p-4 bg-primary/10 rounded-lg border-2 border-primary/20">
        <span className="text-sm sm:text-lg font-semibold">Total Amount:</span>
        <span className="text-lg sm:text-2xl font-bold text-primary">
          ${get(data, "total_amount", 0).toFixed(2)}
        </span>
      </div>
    </div>
  );

  const renderPersonalInfo = () => (
    <div className="space-y-3 sm:space-y-4 animate-in fade-in slide-in-from-right-4 duration-500">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm">Full Name *</FormLabel>
              <FormControl>
                <Input
                  placeholder="John Doe"
                  className="h-10 sm:h-11"
                  {...field}
                  onChange={(e) => {
                    const value = e.target.value.replace(/[^a-zA-Z\s]/g, "");
                    field.onChange(value);
                  }}
                />
              </FormControl>
              <FormMessage className="text-xs" />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm">Email Address *</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="john@example.com"
                  className="h-10 sm:h-11"
                  {...field}
                />
              </FormControl>
              <FormMessage className="text-xs" />
            </FormItem>
          )}
        />
      </div>

      <FormField
        control={form.control}
        name="phone"
        render={({ field }) => (
          <FormItem>
            <FormLabel className="text-sm">Phone Number *</FormLabel>
            <FormControl>
              <Input
                placeholder="123-456-7890"
                className="h-10 sm:h-11"
                {...field}
                onChange={(e) => {
                  const formatted = formatPhoneNumber(e.target.value);
                  field.onChange(formatted);
                }}
                maxLength={12}
              />
            </FormControl>
            <FormMessage className="text-xs" />
          </FormItem>
        )}
      />
    </div>
  );

  const renderShippingAddress = () => (
    <div className="space-y-3 sm:space-y-4 animate-in fade-in slide-in-from-right-4 duration-500">
      <FormField
        control={form.control}
        name="selectedAddressId"
        render={({ field }) => (
          <FormItem>
            <FormControl>
              <RadioGroup
                onValueChange={field.onChange}
                value={field.value}
                className="space-y-2 sm:space-y-3"
              >
                {get(data, "saved_addresses", []).map((address) => {
                  const addressId = get(address, "id", "");
                  const street = get(address, "street", "");
                  const city = get(address, "city", "");
                  const state = get(address, "state", "");
                  const zipCode = get(address, "zip_code", "");
                  const isDefault = get(address, "is_default", false);

                  return (
                    <div
                      key={addressId}
                      className={`relative flex items-start space-x-2.5 sm:space-x-3 p-3 sm:p-4 border-2 rounded-lg cursor-pointer transition-all ${
                        field.value === toString(addressId)
                          ? "border-primary bg-primary/5"
                          : "border-border hover:border-primary/50 hover:bg-muted/50"
                      }`}
                      onClick={() => field.onChange(toString(addressId))}
                    >
                      <RadioGroupItem
                        value={toString(addressId)}
                        id={`address-${addressId}`}
                        className="mt-0.5 sm:mt-1"
                      />
                      <div className="flex-1 space-y-1">
                        <label
                          htmlFor={`address-${addressId}`}
                          className="text-xs sm:text-sm font-medium cursor-pointer"
                        >
                          <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2">
                            <span className="break-words">
                              {street}, {city}, {state} {zipCode}
                            </span>
                            {isDefault && (
                              <Badge
                                variant="default"
                                className="text-[10px] sm:text-xs w-fit"
                              >
                                Default
                              </Badge>
                            )}
                          </div>
                        </label>
                      </div>
                    </div>
                  );
                })}
              </RadioGroup>
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );

  const renderPaymentMethod = () => (
    <div className="space-y-3 sm:space-y-4 animate-in fade-in slide-in-from-right-4 duration-500">
      <FormField
        control={form.control}
        name="paymentMethod"
        render={({ field }) => (
          <FormItem>
            <FormControl>
              <RadioGroup
                onValueChange={field.onChange}
                value={field.value}
                className="space-y-2 sm:space-y-3"
              >
                {includes(
                  get(data, "allowed_payment_methods", []),
                  "cash_on_delivery"
                ) && (
                  <div
                    className={`flex items-start space-x-2.5 sm:space-x-3 p-3 sm:p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      field.value === "cash_on_delivery"
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/50 hover:bg-muted/50"
                    }`}
                    onClick={() => field.onChange("cash_on_delivery")}
                  >
                    <RadioGroupItem
                      value="cash_on_delivery"
                      id="cod"
                      className="mt-0.5 sm:mt-1"
                    />
                    <label htmlFor="cod" className="flex-1 cursor-pointer">
                      <div className="font-medium text-xs sm:text-sm">
                        Cash on Delivery
                      </div>
                      <p className="text-[10px] sm:text-xs text-muted-foreground mt-0.5 sm:mt-1">
                        Pay when your order is delivered
                      </p>
                    </label>
                  </div>
                )}

                {includes(
                  get(data, "allowed_payment_methods", []),
                  "credit_card"
                ) && (
                  <div
                    className={`flex items-start space-x-2.5 sm:space-x-3 p-3 sm:p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      field.value === "credit_card"
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/50 hover:bg-muted/50"
                    }`}
                    onClick={() => field.onChange("credit_card")}
                  >
                    <RadioGroupItem
                      value="credit_card"
                      id="credit_card"
                      className="mt-0.5 sm:mt-1"
                    />
                    <label
                      htmlFor="credit_card"
                      className="flex-1 cursor-pointer"
                    >
                      <div className="font-medium text-xs sm:text-sm">
                        Credit Card
                      </div>
                      <p className="text-[10px] sm:text-xs text-muted-foreground mt-0.5 sm:mt-1">
                        Pay securely with your credit card
                      </p>
                    </label>
                  </div>
                )}
              </RadioGroup>
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      {paymentMethod === "credit_card" && (
        <div className="mt-3 sm:mt-4 p-3 sm:p-4 bg-muted/50 rounded-lg border border-border space-y-3 sm:space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
          <h4 className="text-xs sm:text-sm font-semibold">
            Credit Card Details
          </h4>

          <FormField
            control={form.control}
            name="cardHolderName"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm">Cardholder Name *</FormLabel>
                <FormControl>
                  <Input
                    placeholder="John Doe"
                    className="h-10 sm:h-11"
                    {...field}
                    onChange={(e) => {
                      const value = e.target.value.replace(/[^a-zA-Z\s]/g, "");
                      field.onChange(value);
                    }}
                  />
                </FormControl>
                <FormMessage className="text-xs" />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="cardNumber"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-sm">Card Number *</FormLabel>
                <FormControl>
                  <Input
                    placeholder="1234 5678 9012 3456"
                    className="h-10 sm:h-11"
                    maxLength={19}
                    {...field}
                    onChange={(e) => {
                      const formatted = formatCardNumber(e.target.value);
                      field.onChange(formatted);
                    }}
                  />
                </FormControl>
                <FormMessage className="text-xs" />
              </FormItem>
            )}
          />

          <div className="grid grid-cols-2 gap-3 sm:gap-4">
            <FormField
              control={form.control}
              name="cvv"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm">CVV *</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="123"
                      className="h-10 sm:h-11"
                      maxLength={3}
                      {...field}
                      onChange={(e) => {
                        const value = e.target.value.replace(/\D/g, "");
                        field.onChange(value);
                      }}
                    />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="expiryDate"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-sm">Expiry Date *</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="MM/YY"
                      className="h-10 sm:h-11"
                      maxLength={5}
                      {...field}
                      onChange={(e) => {
                        const formatted = formatExpiryDate(e.target.value);
                        field.onChange(formatted);
                      }}
                    />
                  </FormControl>
                  <FormMessage className="text-xs" />
                </FormItem>
              )}
            />
          </div>
        </div>
      )}
    </div>
  );

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return renderOrderSummary();
      case 2:
        return renderPersonalInfo();
      case 3:
        return renderShippingAddress();
      case 4:
        return renderPaymentMethod();
      default:
        return null;
    }
  };

  return (
    <Card className="w-full border-none bg-transparent">
      <CardHeader className="p-3 sm:p-6 pb-2 sm:pb-3">
        <CardTitle className="text-lg sm:text-2xl font-bold">
          Secure Checkout
        </CardTitle>
        <p className="text-xs sm:text-sm text-muted-foreground mt-1">
          Complete your purchase in {steps.length} easy steps
        </p>
      </CardHeader>

      <CardContent className="p-3 sm:p-6">
        {renderStepIndicator()}

        <Form {...form}>
          <form className="space-y-4 sm:space-y-6">
            <div className="min-h-[280px] sm:min-h-[350px]">
              {renderStepContent()}
            </div>

            {/* Navigation Buttons */}
            <div className="flex flex-col-reverse sm:flex-row gap-2 sm:gap-3 pt-4 border-t">
              {currentStep > 1 && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={prevStep}
                  className="w-full sm:w-auto sm:flex-none h-11 sm:h-10"
                >
                  <LuChevronLeft className="w-4 h-4 mr-1" />
                  Back
                </Button>
              )}

              {currentStep < steps.length ? (
                <Button
                  type="button"
                  onClick={nextStep}
                  className="w-full sm:flex-1 h-11 sm:h-10"
                >
                  Continue
                  <LuChevronRight className="w-4 h-4 ml-1" />
                </Button>
              ) : (
                <Button
                  type="button"
                  onClick={async () => {
                    const isValid = await validateCurrentStep();
                    if (isValid) {
                      form.handleSubmit(onSubmit)();
                    }
                  }}
                  disabled={isSubmitting}
                  className="w-full sm:flex-1 h-11 sm:h-10 bg-green-600 hover:bg-green-700 text-sm sm:text-base"
                >
                  {isSubmitting ? (
                    "Processing..."
                  ) : (
                    <>
                      <LuCheck className="w-4 h-4 mr-2" />
                      <span className="hidden sm:inline">
                        Complete Order -{" "}
                      </span>
                      <span className="sm:hidden">Complete - </span>$
                      {get(data, "total_amount", 0).toFixed(2)}
                    </>
                  )}
                </Button>
              )}
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

export default CheckoutForm;
