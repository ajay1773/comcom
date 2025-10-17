import { useCallback } from "react";
import { useChatStore } from "@/store/chat-store";
import SignupForm, { type SignupFormData } from "../signup-form";

/**
 * Wrapper component for SignupForm that maintains backward compatibility
 * with the old chat-based signup flow where form data is sent as messages.
 */
const SignupFormChat = () => {
  const { sendMessage } = useChatStore();

  const handleSubmit = useCallback(
    async (data: SignupFormData) => {
      const message = `I would like to create a new account with the following information:
      - Email: ${data.email}
      - Password: ${data.password}
      - First Name: ${data.first_name}
      - Last Name: ${data.last_name}
      - Phone: ${data.phone}
      `;
      await sendMessage(message);
    },
    [sendMessage]
  );

  return <SignupForm onSubmit={handleSubmit} />;
};

export default SignupFormChat;
