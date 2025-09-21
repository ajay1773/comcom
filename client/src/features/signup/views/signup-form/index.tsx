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
import { useCallback } from "react";
import { useChat } from "@/store/chat-store";
import "./style.css";

const formSchema = z.object({
  email: z
    .string()
    .min(1, { message: "Email is required." })
    .email({ message: "Please enter a valid email address." }),
  password: z
    .string()
    .min(1, { message: "Password is required." })
    .min(8, { message: "Password must be at least 8 characters long." })
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, {
      message:
        "Password must contain at least one uppercase letter, one lowercase letter, and one number.",
    }),
  first_name: z
    .string()
    .min(1, { message: "First name is required." })
    .min(2, { message: "First name must be at least 2 characters." })
    .max(50, { message: "First name must not exceed 50 characters." })
    .regex(/^[a-zA-Z\s]*$/, {
      message: "First name can only contain letters and spaces.",
    }),
  last_name: z
    .string()
    .min(1, { message: "Last name is required." })
    .min(2, { message: "Last name must be at least 2 characters." })
    .max(50, { message: "Last name must not exceed 50 characters." })
    .regex(/^[a-zA-Z\s]*$/, {
      message: "Last name can only contain letters and spaces.",
    }),
  phone: z
    .string()
    .min(1, { message: "Phone number is required." })
    .regex(/^\+?[\d\s\-()]+$/, {
      message: "Please enter a valid phone number.",
    })
    .min(10, { message: "Phone number must be at least 10 digits." }),
});

type SignupFormData = z.infer<typeof formSchema>;

const SignupForm = () => {
  const { sendMessage } = useChat();

  const form = useForm<SignupFormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
      first_name: "",
      last_name: "",
      phone: "",
    },
  });

  const formatPhoneNumber = useCallback((value: string) => {
    const digits = value.replace(/\D/g, "");
    if (digits.length <= 3) return digits;
    if (digits.length <= 6) return `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
    return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(
      6,
      10
    )}`;
  }, []);

  const onSubmit = useCallback(
    async (data: SignupFormData) => {
      const message = `I would like to create a new account with the following information:
      - Email: ${data.email}
      - Password: ${data.password}
      - First Name: ${data.first_name}
      - Last Name: ${data.last_name}
      - Phone: ${data.phone}
      `;
      await sendMessage(message);
      // Handle form submission
    },
    [sendMessage]
  );

  return (
    <Card className="w-full max-w-md mx-auto border-none">
      <CardHeader>
        <CardTitle>Sign Up</CardTitle>
      </CardHeader>
      {/* <div className="form-card-icon">
        <LuBrainCircuit className="w-8 h-8 text-white" />
      </div> */}
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="flex gap-4">
              <FormField
                control={form.control}
                name="first_name"
                render={({ field }) => (
                  <FormItem className="flex-1 min-h-[85px] relative">
                    <FormLabel>First Name</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="John"
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
                    <FormMessage className="absolute -bottom-2" />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="last_name"
                render={({ field }) => (
                  <FormItem className="flex-1 min-h-[85px] relative">
                    <FormLabel>Last Name</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="Doe"
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
                    <FormMessage className="absolute -bottom-2" />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem className="min-h-[85px] relative">
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      placeholder="john.doe@example.com"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="absolute -bottom-2" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="phone"
              render={({ field }) => (
                <FormItem className="min-h-[85px] relative">
                  <FormLabel>Phone Number</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="(555) 123-4567"
                      maxLength={14}
                      {...field}
                      onChange={(e) => {
                        const formatted = formatPhoneNumber(e.target.value);
                        field.onChange(formatted);
                      }}
                    />
                  </FormControl>
                  <FormMessage className="absolute -bottom-2" />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem className="min-h-[85px] relative">
                  <FormLabel>Password</FormLabel>
                  <FormControl>
                    <Input
                      type="password"
                      placeholder="Enter your password"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage className="absolute -bottom-2" />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full mt-4">
              Create Account
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

export default SignupForm;
