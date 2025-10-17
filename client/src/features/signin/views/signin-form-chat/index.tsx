import { useCallback } from "react";
import { useChatStore } from "@/store/chat-store";
import SigninForm, { type LoginFormData } from "../signin-form";

/**
 * Wrapper component for SigninForm that maintains backward compatibility
 * with the old chat-based signin flow where credentials are sent as messages.
 */
const SigninFormChat = () => {
  const { sendMessage } = useChatStore();

  const handleSubmit = useCallback(
    async (data: LoginFormData) => {
      const message = `Here is my login credentials:
- Email: ${data.email}
- Password: ${data.password}
`;
      await sendMessage(message);
    },
    [sendMessage]
  );

  return <SigninForm onSubmit={handleSubmit} />;
};

export default SigninFormChat;
