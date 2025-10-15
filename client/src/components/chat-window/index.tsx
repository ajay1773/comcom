import { useChatStore } from "../../store/chat-store";
import SignedInChatWindow from "./signed-in-chat-window";
import SignedOutChatWindow from "./signed-out-chat-window";

const ChatWindow = () => {
  const { isLoggedIn } = useChatStore();
  const loggedIn = isLoggedIn();

  // Simple wrapper - render appropriate component based on login status
  return loggedIn ? <SignedInChatWindow /> : <SignedOutChatWindow />;
};

export default ChatWindow;
