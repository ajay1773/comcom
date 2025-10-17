import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import SigninForm, { type LoginFormData } from "../signin-form";
import { signinUser } from "../../api/signin";
import { useChatStore } from "@/store/chat-store";
import { toast } from "sonner";

interface SigninModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const SigninModal = ({ open, onOpenChange }: SigninModalProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const { setUserDetails } = useChatStore();

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

        // Close modal
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
};

export default SigninModal;
