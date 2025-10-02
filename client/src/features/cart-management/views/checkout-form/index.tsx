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
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import type { CheckoutUIProviderData } from "@/features/cart-management/types";
import { useChatStore } from "@/store/chat-store";

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

const CheckoutForm: FC<CheckoutFormProps> = ({ data }) => {
  const { sendMessage } = useChatStore();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<CheckoutFormData>({
    resolver: zodResolver(checkoutFormSchema),
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
  const formValues = form.watch();

  // Check if all required fields are filled
  const isFormValid = useCallback(() => {
    const { name, email, phone, selectedAddressId, paymentMethod } = formValues;

    // Basic required fields
    const basicFieldsValid =
      !isEmpty(name) &&
      !isEmpty(email) &&
      !isEmpty(phone) &&
      !isEmpty(selectedAddressId) &&
      !isEmpty(paymentMethod);

    // If credit card is selected, check credit card fields
    if (paymentMethod === "credit_card") {
      const { cardHolderName, cardNumber, cvv, expiryDate } = formValues;
      const creditCardFieldsValid =
        !isEmpty(cardHolderName) &&
        !isEmpty(cardNumber) &&
        !isEmpty(cvv) &&
        !isEmpty(expiryDate);
      return basicFieldsValid && creditCardFieldsValid;
    }

    return basicFieldsValid;
  }, [formValues]);

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

  return (
    <div className="flex h-full overflow-y-auto">
      <Card className="w-full max-w-4xl mx-auto border-none bg-transparent">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Checkout</CardTitle>
        </CardHeader>
        <CardContent className="space-y-8">
          {/* Products Section */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Order Summary</h3>
            <div className="space-y-3">
              {get(data, "product_items", []).map((item) => {
                const productId = get(item, "product_id", "");
                const size = get(item, "size", "");
                const color = get(item, "color", "");
                const productDetails = get(item, "product_details", {});
                const images = JSON.parse(
                  get(productDetails, "images", "{}") as string
                );
                const thumbnailSrc = get(images, "thumbnail", "");
                const productName = get(productDetails, "name", "");
                const brandName = get(productDetails, "brand", "");
                const totalPrice = get(item, "total_price", 0);
                const quantity = get(item, "quantity", 0);

                return (
                  <div
                    key={`${productId}-${size}-${color}`}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center gap-4">
                      <img
                        src={thumbnailSrc}
                        alt={productName}
                        className="w-16 h-16 object-cover rounded-lg"
                      />
                      <div className="flex flex-col justify-between">
                        <h4 className="font-medium">{productName}</h4>
                        <p className="text-sm text-gray-600">{brandName}</p>
                        <div className="flex gap-2">
                          {!isEmpty(size) && (
                            <Badge variant="secondary" className="text-xs">
                              Size: {size}
                            </Badge>
                          )}
                          {!isEmpty(color) && (
                            <Badge variant="secondary" className="text-xs">
                              Color: {color}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col justify-between">
                      <p className="font-medium">${totalPrice.toFixed(2)}</p>
                      <p className="text-sm text-gray-600">Qty: {quantity}</p>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between items-center pt-4 border-t">
              <span className="text-lg font-semibold">Total:</span>
              <span className="text-xl font-bold">
                ${get(data, "total_amount", 0).toFixed(2)}
              </span>
            </div>
          </div>

          <Separator />

          {/* Checkout Form */}
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              {/* Personal Information Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Personal Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <FormField
                    control={form.control}
                    name="name"
                    render={({ field }) => (
                      <FormItem className="space-y-2">
                        <FormLabel>Full Name *</FormLabel>
                        <FormControl>
                          <Input
                            placeholder="John Doe"
                            {...field}
                            onChange={(e) => {
                              const value = e.target.value.replace(
                                /[^a-zA-Z\s]/g,
                                ""
                              );
                              field.onChange(value);
                            }}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="email"
                    render={({ field }) => (
                      <FormItem className="space-y-2">
                        <FormLabel>Email Address *</FormLabel>
                        <FormControl>
                          <Input
                            type="email"
                            placeholder="john@example.com"
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="phone"
                  render={({ field }) => (
                    <FormItem className="space-y-2">
                      <FormLabel>Phone Number *</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="123-456-7890"
                          {...field}
                          onChange={(e) => {
                            const formatted = formatPhoneNumber(e.target.value);
                            field.onChange(formatted);
                          }}
                          maxLength={12}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <Separator />

              {/* Shipping Address Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Shipping Address</h3>
                <FormField
                  control={form.control}
                  name="selectedAddressId"
                  render={({ field }) => (
                    <FormItem className="space-y-3">
                      <FormControl>
                        <RadioGroup
                          onValueChange={field.onChange}
                          value={field.value}
                          className="space-y-3"
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
                                className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-gray-700/10 transition-colors"
                              >
                                <RadioGroupItem
                                  value={toString(addressId)}
                                  id={`address-${addressId}`}
                                  className="mt-1"
                                />
                                <div className="flex-1 space-y-1">
                                  <label
                                    htmlFor={`address-${addressId}`}
                                    className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                                  >
                                    <div className="flex items-center gap-2">
                                      <span>
                                        {street}, {city}, {state} {zipCode}
                                      </span>
                                      {isDefault && (
                                        <Badge
                                          variant="default"
                                          className="text-xs"
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

              <Separator />

              {/* Payment Method Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Payment Method</h3>
                <FormField
                  control={form.control}
                  name="paymentMethod"
                  render={({ field }) => (
                    <FormItem className="space-y-3">
                      <FormControl>
                        <RadioGroup
                          onValueChange={field.onChange}
                          value={field.value}
                          className="space-y-3"
                        >
                          {includes(
                            get(data, "allowed_payment_methods", []),
                            "cash_on_delivery"
                          ) && (
                            <div className="flex items-center space-x-3 p-4 border rounded-lg hover:bg-gray-700/10 transition-colors">
                              <RadioGroupItem
                                value="cash_on_delivery"
                                id="cod"
                              />
                              <label
                                htmlFor="cod"
                                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex-1"
                              >
                                Cash on Delivery
                                <p className="text-xs text-gray-600 mt-1">
                                  Pay when your order is delivered
                                </p>
                              </label>
                            </div>
                          )}

                          {includes(
                            get(data, "allowed_payment_methods", []),
                            "credit_card"
                          ) && (
                            <div className="flex items-start space-x-3 p-4 border rounded-lg hover:bg-gray-700/10 transition-colors">
                              <RadioGroupItem
                                value="credit_card"
                                id="credit_card"
                                className="mt-1"
                              />
                              <label
                                htmlFor="credit_card"
                                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer flex-1"
                              >
                                Credit Card
                                <p className="text-xs text-gray-600 mt-1">
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

                {/* Credit Card Details (shown when credit card is selected) */}
                {paymentMethod === "credit_card" && (
                  <div className="mt-6 p-4 bg-gray-700/10 rounded-lg space-y-4">
                    <h4 className="font-medium">Credit Card Details</h4>

                    <FormField
                      control={form.control}
                      name="cardHolderName"
                      render={({ field }) => (
                        <FormItem className="space-y-2">
                          <FormLabel>Cardholder Name *</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="John Doe"
                              {...field}
                              onChange={(e) => {
                                const value = e.target.value.replace(
                                  /[^a-zA-Z\s]/g,
                                  ""
                                );
                                field.onChange(value);
                              }}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="cardNumber"
                      render={({ field }) => (
                        <FormItem className="space-y-2">
                          <FormLabel>Card Number *</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="1234 5678 9012 3456"
                              maxLength={19}
                              {...field}
                              onChange={(e) => {
                                const formatted = formatCardNumber(
                                  e.target.value
                                );
                                field.onChange(formatted);
                              }}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="cvv"
                        render={({ field }) => (
                          <FormItem className="space-y-2">
                            <FormLabel>CVV *</FormLabel>
                            <FormControl>
                              <Input
                                type="password"
                                placeholder="123"
                                maxLength={3}
                                {...field}
                                onChange={(e) => {
                                  const value = e.target.value.replace(
                                    /\D/g,
                                    ""
                                  );
                                  field.onChange(value);
                                }}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />

                      <FormField
                        control={form.control}
                        name="expiryDate"
                        render={({ field }) => (
                          <FormItem className="space-y-2">
                            <FormLabel>Expiry Date *</FormLabel>
                            <FormControl>
                              <Input
                                placeholder="MM/YY"
                                maxLength={5}
                                {...field}
                                onChange={(e) => {
                                  const formatted = formatExpiryDate(
                                    e.target.value
                                  );
                                  field.onChange(formatted);
                                }}
                              />
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <div className="pt-6 border-t">
                <Button
                  type="submit"
                  className="w-full h-12 text-lg font-semibold"
                  disabled={isSubmitting || !isFormValid()}
                >
                  {isSubmitting
                    ? "Processing..."
                    : `Pay & Checkout - $${get(data, "total_amount", 0).toFixed(
                        2
                      )}`}
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
};

export default CheckoutForm;
