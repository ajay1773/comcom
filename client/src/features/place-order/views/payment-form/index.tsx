"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
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
import type { PaymentDetails } from "../../types";
import { useCallback } from "react";
import { Separator } from "@/components/ui/separator";
import { useChat } from "@/store/chat-store";

const formSchema = z.object({
  userName: z
    .string()
    .min(2, { message: "Name must be at least 2 characters." })
    .max(50, { message: "Name must not exceed 50 characters." })
    .regex(/^[a-zA-Z\s]*$/, {
      message: "Name can only contain letters and spaces.",
    }),
  cardNumber: z
    .string()
    .min(19, { message: "Card number must be 16 digits." })
    .max(19, { message: "Card number must be 16 digits." })
    .regex(/^\d{4}\s\d{4}\s\d{4}\s\d{4}$/, {
      message: "Invalid card number format.",
    }),
  cvv: z
    .string()
    .min(3, { message: "CVV must be 3 digits." })
    .max(3, { message: "CVV must be 3 digits." })
    .regex(/^\d{3}$/, { message: "CVV must be 3 digits." }),
  expiryDate: z
    .string()
    .regex(/^(0[1-9]|1[0-2])\/(0[1-9]|[12]\d|3[01])\/\d{4}$/, {
      message: "Invalid date format (mm/dd/yyyy).",
    })
    .refine(
      (date) => {
        const [month, day, year] = date.split("/").map(Number);
        const inputDate = new Date(year, month - 1, day);
        const today = new Date();
        return inputDate > today;
      },
      { message: "Expiry date must be in the future." }
    ),
});

type PaymentFormData = z.infer<typeof formSchema>;

type PaymentFormProps = {
  details: PaymentDetails;
};

const PaymentForm = ({ details }: PaymentFormProps) => {
  const { sendMessage } = useChat();

  const form = useForm<PaymentFormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      userName: "",
      cardNumber: "",
      cvv: "",
      expiryDate: "",
    },
  });

  const formatCardNumber = useCallback((value: string) => {
    const digits = value.replace(/\D/g, "");
    const groups = digits.match(/.{1,4}/g) || [];
    return groups.join(" ").substr(0, 19);
  }, []);

  const formatExpiryDate = useCallback((value: string) => {
    const digits = value.replace(/\D/g, "");
    if (digits.length <= 2) return digits;
    if (digits.length <= 4) return `${digits.slice(0, 2)}/${digits.slice(2)}`;
    return `${digits.slice(0, 2)}/${digits.slice(2, 4)}/${digits.slice(4, 8)}`;
  }, []);

  const onSubmit = useCallback(
    async (data: PaymentFormData) => {
      const message = `I would like to pay for ${details.selected_product.name} (${details.selected_product.brand}) with the following credit card details:
- Name on Card: ${data.userName}
- Card Number: ${data.cardNumber}
- CVV: ${data.cvv}
- Expiry Date: ${data.expiryDate}
`;
      await sendMessage(message);
      // Handle form submission
    },
    [details.selected_product.name, details.selected_product.brand, sendMessage]
  );

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Payment Form</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-8">
          <div className="flex w-full items-center justify-between">
            <div className="flex gap-2">
              <img
                className="rounded-lg w-12 h-12"
                src={details?.selected_product?.images?.thumbnail || ""}
                alt={details?.selected_product?.name || ""}
              />
              <div className="flex flex-col gap-1">
                <p className="text-lg font-semibold">
                  {details?.selected_product?.name}
                </p>
                <span className="flex items-center justify-baseline gap-1">
                  <p className="text-sm font-light">
                    {details.selected_product.brand}
                  </p>
                </span>
              </div>
            </div>
            <div className="flex flex-col gap-1 items-end">
              <p className="text-md font-medium">
                ${Math.round(details?.selected_product?.min_price)}
              </p>
              <p className="text-sm font-light">Quantity: 1</p>
            </div>
          </div>

          <Separator />

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="userName"
                render={({ field }) => (
                  <FormItem className="min-h-[85px] relative">
                    <FormLabel>Name on Card</FormLabel>
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
                    <FormMessage className="absolute -bottom-2  " />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="cardNumber"
                render={({ field }) => (
                  <FormItem className="min-h-[85px] relative">
                    <FormLabel>Card Number</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="1234 5678 9012 3456"
                        maxLength={19}
                        {...field}
                        onChange={(e) => {
                          const formatted = formatCardNumber(e.target.value);
                          field.onChange(formatted);
                        }}
                      />
                    </FormControl>
                    <FormMessage className="absolute -bottom-2  " />
                  </FormItem>
                )}
              />

              <div className="flex gap-4">
                <FormField
                  control={form.control}
                  name="cvv"
                  render={({ field }) => (
                    <FormItem className="flex-1 min-h-[85px] relative">
                      <FormLabel>CVV</FormLabel>
                      <FormControl>
                        <Input
                          type="password"
                          placeholder="123"
                          maxLength={3}
                          {...field}
                          onChange={(e) => {
                            const value = e.target.value.replace(/\D/g, "");
                            field.onChange(value);
                          }}
                        />
                      </FormControl>
                      <FormMessage className="absolute -bottom-2  " />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="expiryDate"
                  render={({ field }) => (
                    <FormItem className="flex-1 min-h-[85px] relative">
                      <FormLabel>Expiry Date</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="MM/DD/YYYY"
                          maxLength={10}
                          {...field}
                          onChange={(e) => {
                            const formatted = formatExpiryDate(e.target.value);
                            field.onChange(formatted);
                          }}
                        />
                      </FormControl>
                      <FormMessage className="absolute -bottom-2  " />
                    </FormItem>
                  )}
                />
              </div>

              <Button type="submit" className="w-full mt-4">
                Pay ${details.price_breakdown.total}
              </Button>
            </form>
          </Form>
        </div>
      </CardContent>
    </Card>
  );
};

export default PaymentForm;
