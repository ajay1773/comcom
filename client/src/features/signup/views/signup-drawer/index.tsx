"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { Button } from "@/components/ui/button";
import SignupForm, { type SignupFormData } from "../signup-form";
import { signupUser } from "../../api/signup";
import { useChatStore } from "@/store/chat-store";
import { toast } from "sonner";
import { useMediaQuery } from "@/hooks/use-media-query";

interface SignupDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const SignupDrawer = ({ open, onOpenChange }: SignupDrawerProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const { setUserDetails } = useChatStore();
  const isDesktop = useMediaQuery("(min-width: 768px)");

  const handleSubmit = async (data: SignupFormData) => {
    setIsLoading(true);
    try {
      const response = await signupUser(data);

      if (response.success && response.token && response.user) {
        // Store token and user details
        localStorage.setItem("jwt_token", response.token);
        localStorage.setItem("user_details", JSON.stringify(response.user));

        // Update store
        setUserDetails(JSON.stringify(response.user));

        // Show success toast
        toast.success("Account created successfully!", {
          description: `Welcome, ${response.user.first_name}! Your account has been created.`,
        });

        // Close drawer/dialog
        onOpenChange(false);
      } else {
        toast.error("Sign up failed", {
          description: response.message || "Please try again.",
        });
      }
    } catch (error) {
      console.error("Sign up error:", error);

      // Check for specific error messages
      const errorMessage =
        error instanceof Error ? error.message : "Please try again.";

      if (errorMessage.includes("already exists")) {
        toast.error("Account already exists", {
          description:
            "An account with this email already exists. Please sign in instead.",
        });
      } else {
        toast.error("Sign up failed", {
          description: errorMessage,
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isDesktop) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create Your Account</DialogTitle>
            <DialogDescription>
              Sign up to start shopping and manage your orders
            </DialogDescription>
          </DialogHeader>
          <SignupForm onSubmit={handleSubmit} isLoading={isLoading} />
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <DrawerHeader className="text-left">
          <DrawerTitle>Create Your Account</DrawerTitle>
          <DrawerDescription>
            Sign up to start shopping and manage your orders
          </DrawerDescription>
        </DrawerHeader>
        <div className="px-4 max-h-[70vh] overflow-y-auto">
          <SignupForm onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
        <DrawerFooter className="pt-2">
          <DrawerClose asChild>
            <Button variant="outline">Cancel</Button>
          </DrawerClose>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
};

export default SignupDrawer;
