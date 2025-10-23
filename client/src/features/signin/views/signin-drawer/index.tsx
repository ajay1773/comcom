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
import SigninForm, { type LoginFormData } from "../signin-form";
import { signinUser } from "../../api/signin";
import { useChatStore } from "@/store/chat-store";
import { toast } from "sonner";
import { useMediaQuery } from "@/hooks/use-media-query";

interface SigninDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const SigninDrawer = ({ open, onOpenChange }: SigninDrawerProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const { setUserDetails } = useChatStore();
  const isDesktop = useMediaQuery("(min-width: 768px)");

  const handleSubmit = async (credentials: LoginFormData) => {
    setIsLoading(true);
    try {
      const response = await signinUser(credentials);

      if (response.success && response.token && response.user) {
        // Store token and user details
        localStorage.setItem("jwt_token", response.token);
        localStorage.setItem("user_details", JSON.stringify(response.user));

        // Update store
        setUserDetails(JSON.stringify(response.user));

        // Show success toast
        toast.success("Sign in successful!", {
          description: `Welcome back, ${
            response.user.first_name || response.user.email
          }!`,
        });

        // Close drawer/dialog
        onOpenChange(false);
      } else {
        toast.error("Sign in failed", {
          description: response.message || "Please try again.",
        });
      }
    } catch (error) {
      console.error("Sign in error:", error);
      toast.error("Sign in failed", {
        description:
          error instanceof Error
            ? error.message
            : "Please check your credentials and try again.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  if (isDesktop) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Welcome Back</DialogTitle>
            <DialogDescription>
              Sign in to your account to continue shopping
            </DialogDescription>
          </DialogHeader>
          <SigninForm onSubmit={handleSubmit} isLoading={isLoading} />
        </DialogContent>
      </Dialog>
    );
  }

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent>
        <DrawerHeader className="text-left">
          <DrawerTitle>Welcome Back</DrawerTitle>
          <DrawerDescription>
            Sign in to your account to continue shopping
          </DrawerDescription>
        </DrawerHeader>
        <div className="px-4 max-h-[70vh] overflow-y-auto">
          <SigninForm onSubmit={handleSubmit} isLoading={isLoading} />
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

export default SigninDrawer;
