"use client";

import React, { useCallback } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
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
import { Label } from "@/components/ui/label";
import type { UserAddress } from "../../types";

const formSchema = z.object({
  type: z.enum(["home", "work", "other"]),
  street: z
    .string()
    .min(1, { message: "Street address is required." })
    .min(5, { message: "Street address must be at least 5 characters." })
    .max(200, { message: "Street address must not exceed 200 characters." }),
  city: z
    .string()
    .min(1, { message: "City is required." })
    .min(2, { message: "City must be at least 2 characters." })
    .max(100, { message: "City must not exceed 100 characters." })
    .regex(/^[a-zA-Z\s\-'.]*$/, {
      message:
        "City can only contain letters, spaces, hyphens, apostrophes, and periods.",
    }),
  state: z
    .string()
    .min(1, { message: "State is required." })
    .min(2, { message: "State must be at least 2 characters." })
    .max(100, { message: "State must not exceed 100 characters." })
    .regex(/^[a-zA-Z\s\-'.]*$/, {
      message:
        "State can only contain letters, spaces, hyphens, apostrophes, and periods.",
    }),
  zip_code: z
    .string()
    .min(1, { message: "ZIP code is required." })
    .regex(/^\d{5}(-\d{4})?$/, {
      message: "Please enter a valid ZIP code (e.g., 12345 or 12345-6789).",
    }),
  country: z
    .string()
    .min(1, { message: "Country is required." })
    .min(2, { message: "Country must be at least 2 characters." })
    .max(100, { message: "Country must not exceed 100 characters." })
    .regex(/^[a-zA-Z\s\-'.]*$/, {
      message:
        "Country can only contain letters, spaces, hyphens, apostrophes, and periods.",
    }),
  is_default: z.boolean(),
});

type AddressFormData = z.infer<typeof formSchema>;

interface AddressFormProps {
  initialData?: UserAddress | null;
  onSubmit: (data: Omit<UserAddress, "id">) => void;
  onCancel: () => void;
}

const AddressForm: React.FC<AddressFormProps> = ({
  initialData,
  onSubmit,
  onCancel,
}) => {
  const form = useForm<AddressFormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      type: (initialData?.type as "home" | "work" | "other") || "other",
      street: initialData?.street || "",
      city: initialData?.city || "",
      state: initialData?.state || "",
      zip_code: initialData?.zip_code || "",
      country: initialData?.country || "",
      is_default: initialData?.is_default || false,
    },
  });

  const formatZipCode = useCallback((value: string) => {
    const digits = value.replace(/\D/g, "");
    if (digits.length <= 5) return digits;
    return `${digits.slice(0, 5)}-${digits.slice(5, 9)}`;
  }, []);

  const handleSubmit = useCallback(
    (data: AddressFormData) => {
      onSubmit(data);
    },
    [onSubmit]
  );

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="type"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Address Type</FormLabel>
              <FormControl>
                <RadioGroup
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                  className="flex flex-row space-x-6"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="home" id="home" />
                    <Label htmlFor="home" className="capitalize">
                      Home
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="work" id="work" />
                    <Label htmlFor="work" className="capitalize">
                      Work
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="other" id="other" />
                    <Label htmlFor="other" className="capitalize">
                      Other
                    </Label>
                  </div>
                </RadioGroup>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="street"
          render={({ field }) => (
            <FormItem className="min-h-[85px] relative">
              <FormLabel>Street Address</FormLabel>
              <FormControl>
                <Input placeholder="123 Main Street, Apt 4B" {...field} />
              </FormControl>
              <FormMessage className="absolute -bottom-2" />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="city"
            render={({ field }) => (
              <FormItem className="min-h-[85px] relative">
                <FormLabel>City</FormLabel>
                <FormControl>
                  <Input
                    placeholder="New York"
                    {...field}
                    onChange={(e) => {
                      const value = e.target.value.replace(
                        /[^a-zA-Z\s\-'.]/g,
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
            name="state"
            render={({ field }) => (
              <FormItem className="min-h-[85px] relative">
                <FormLabel>State</FormLabel>
                <FormControl>
                  <Input
                    placeholder="NY"
                    {...field}
                    onChange={(e) => {
                      const value = e.target.value.replace(
                        /[^a-zA-Z\s\-'.]/g,
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

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="zip_code"
            render={({ field }) => (
              <FormItem className="min-h-[85px] relative">
                <FormLabel>ZIP Code</FormLabel>
                <FormControl>
                  <Input
                    placeholder="10001"
                    maxLength={10}
                    {...field}
                    onChange={(e) => {
                      const formatted = formatZipCode(e.target.value);
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
            name="country"
            render={({ field }) => (
              <FormItem className="min-h-[85px] relative">
                <FormLabel>Country</FormLabel>
                <FormControl>
                  <Input
                    placeholder="United States"
                    {...field}
                    onChange={(e) => {
                      const value = e.target.value.replace(
                        /[^a-zA-Z\s\-'.]/g,
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
          name="is_default"
          render={({ field }) => (
            <FormItem className="flex flex-row items-center space-x-3 space-y-0">
              <FormControl>
                <input
                  type="checkbox"
                  checked={field.value}
                  onChange={field.onChange}
                  className="h-4 w-4 rounded border border-input bg-background"
                />
              </FormControl>
              <FormLabel className="text-sm font-normal">
                Set as default address
              </FormLabel>
            </FormItem>
          )}
        />

        <div className="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 space-y-2 space-y-reverse sm:space-y-0">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            className="w-full sm:w-auto"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            className="w-full sm:w-auto"
            disabled={form.formState.isSubmitting}
          >
            {form.formState.isSubmitting
              ? "Saving..."
              : initialData
              ? "Update Address"
              : "Add Address"}
          </Button>
        </div>
      </form>
    </Form>
  );
};

export default AddressForm;
