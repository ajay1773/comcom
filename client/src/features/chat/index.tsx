import { useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import Sidebar from "../../components/sidebar";
import ChatWindow from "../../components/chat-window";
import { useChatStore } from "../../store/chat-store";

const Chat = () => {
  const { chatId } = useParams<{ chatId?: string }>();
  const {
    loadConversationById,
    resetChat,
    isLoggedIn: checkIsLoggedIn,
  } = useChatStore();

  // Track the last processed chat ID to prevent infinite loops
  const lastProcessedId = useRef<string | undefined>(undefined);

  // Check if user is logged in using store helper
  const isLoggedIn = checkIsLoggedIn();

  useEffect(() => {
    const handleChatFromUrl = async () => {
      // Prevent processing the same chat ID multiple times
      if (lastProcessedId.current === chatId) {
        return;
      }

      lastProcessedId.current = chatId;

      // For logged OUT users: maintain context within session, just don't show conversations
      if (!isLoggedIn) {
        // Don't reset chat - let them keep context within the session
        // Context is cleared only on page reload (which resets the store)
        return;
      }

      // For logged IN users:
      if (chatId) {
        // Load specific conversation from URL (/chat/c/:chatId)
        const id = parseInt(chatId, 10);
        if (!isNaN(id)) {
          try {
            await loadConversationById(id);
          } catch (error) {
            console.error("Failed to load conversation from URL:", error);
            // Reset the ref so we can try again if needed
            lastProcessedId.current = undefined;
            // Reset chat on error
            resetChat();
          }
        }
      } else {
        // No chatId in URL (/chat) - show empty window
        resetChat();
      }
    };

    handleChatFromUrl();
  }, [chatId, isLoggedIn]); // Depend on chatId and login status

  return (
    <div className="flex w-full h-full">
      {/* Only show sidebar for logged-in users */}
      {isLoggedIn && <Sidebar />}
      <ChatWindow />
    </div>
  );
};

export default Chat;
