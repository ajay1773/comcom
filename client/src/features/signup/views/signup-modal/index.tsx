import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import SignupForm, { type SignupFormData } from "../signup-form";
import { signupUser } from "../../api/signup";
import { useChatStore } from "@/store/chat-store";
import { toast } from "sonner";

interface SignupModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const SignupModal = ({ open, onOpenChange }: SignupModalProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const { setUserDetails } = useChatStore();

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

        // Close modal
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
};

export default SignupModal;
