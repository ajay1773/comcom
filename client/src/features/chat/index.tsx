import { useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import Sidebar from "../../components/sidebar";
import ChatWindow from "../../components/chat-window";
import { useChatStore } from "../../store/chat-store";

const Chat = () => {
  const { conversationId } = useParams<{ conversationId?: string }>();
  const { loadConversationById, createNewConversation, currentConversation } =
    useChatStore();

  // Track the last processed conversation ID to prevent infinite loops
  const lastProcessedId = useRef<string | undefined>(undefined);

  useEffect(() => {
    const handleConversationFromUrl = async () => {
      // Prevent processing the same conversation ID multiple times
      if (lastProcessedId.current === conversationId) {
        return;
      }

      lastProcessedId.current = conversationId;

      if (conversationId && conversationId !== "new") {
        // Load specific conversation from URL
        const id = parseInt(conversationId, 10);
        if (!isNaN(id)) {
          // Only load if it's not already the current conversation
          if (currentConversation?.id !== id) {
            try {
              await loadConversationById(id);
            } catch (error) {
              console.error("Failed to load conversation from URL:", error);
              // Reset the ref so we can try again if needed
              lastProcessedId.current = undefined;
            }
          }
        }
      } else if (!conversationId || conversationId === "new") {
        // Create new conversation if no ID or "new" in URL
        if (!currentConversation) {
          try {
            await createNewConversation();
          } catch (error) {
            console.error("Failed to create new conversation:", error);
            // Reset the ref so we can try again if needed
            lastProcessedId.current = undefined;
          }
        }
      }
    };

    handleConversationFromUrl();
  }, [conversationId]); // Only depend on conversationId, not the functions or currentConversation

  return (
    <div className="flex w-full h-full">
      <Sidebar />
      <ChatWindow />
    </div>
  );
};

export default Chat;
