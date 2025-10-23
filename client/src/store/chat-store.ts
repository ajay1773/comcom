import { create } from "zustand";
import type { ChatChunkResponse, Message, ToolStatus } from "../types/chat";
import { EVENT_EMITTER_ADD_WORKFLOW_JSON } from "@/config";
import emitter from "@/core/event-emitter";
import { get as getDetails } from "lodash";

// Conversation types
export interface Conversation {
  id: number;
  thread_id: string;
  user_id: number | null;
  title: string | null;
  created_at: string | null;
  updated_at: string | null;
  last_message_at: string | null;
  message_count: number;
}

// Rate limit types
export interface RateLimitStatus {
  isRateLimited: boolean;
  limitType: "requests" | "tokens" | null;
  message: string | null;
  retryAfter?: number; // seconds
  remainingRequests?: number;
  remainingTokens?: number;
  tokensUsed?: number;
  dailyLimit?: number;
  limit?: number;
  resetTime?: string;
  resetDate?: string;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  currentStreamingMessageId: string | null;
  threadId: string | null;
  toolStatus: ToolStatus | null;
  disfluencyMessage: string | null;
  widgetJson: { template: string; payload: unknown } | null;
  userDetails: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  } | null;

  // Rate limiting
  rateLimitStatus: RateLimitStatus;

  // Conversation management
  conversations: Conversation[];
  currentConversation: Conversation | null;
  conversationsLoading: boolean;

  // Actions
  addMessage: (message: Message) => void;
  updateToolMessage: (
    id: string,
    update: {
      toolStatus?: Message["toolStatus"];
      content?: string;
      endTime?: Date;
    }
  ) => void;
  updateStreamingMessage: (
    id: string,
    update: { content?: string; json?: { template: string; payload: unknown } }
  ) => void;
  finishStreaming: (id: string) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  resetChat: () => void;
  setThreadId: (threadId: string) => void;
  setToolStatus: (status: ToolStatus | null) => void;
  setDisfluencyMessage: (message: string) => void;
  setWidgetJson: (json: { template: string; payload: unknown }) => void;
  setUserDetails: (details: string) => void;
  logout: () => void;

  // Rate limiting actions
  setRateLimitStatus: (status: RateLimitStatus) => void;
  clearRateLimitError: () => void;
  checkRateLimitStatus: (apiBaseUrl?: string) => Promise<void>;

  // Async Actions
  sendMessage: (content: string, apiBaseUrl?: string) => Promise<void>;
  loadConversationHistory: (
    threadId: string,
    apiBaseUrl?: string
  ) => Promise<void>;

  // Conversation management actions
  loadConversations: (apiBaseUrl?: string) => Promise<void>;
  createNewConversation: (apiBaseUrl?: string) => Promise<string>;
  loadConversationById: (
    conversationId: number,
    apiBaseUrl?: string
  ) => Promise<void>;
  switchConversation: (threadId: string, apiBaseUrl?: string) => Promise<void>;
  switchConversationById: (
    conversationId: number,
    apiBaseUrl?: string
  ) => Promise<void>;
  updateConversationTitle: (
    conversationId: number,
    title: string,
    apiBaseUrl?: string
  ) => Promise<void>;
  deleteConversation: (
    conversationId: number,
    apiBaseUrl?: string
  ) => Promise<void>;

  // Selectors
  getToolMessageById: (id: string) => Message | undefined;
  getActiveToolMessages: () => Message[];
  getCompletedToolMessages: () => Message[];
  getToolMessages: () => Message[];
  getChatMessages: () => Message[];

  // Auth helper
  isLoggedIn: () => boolean;
}

const initialState = {
  messages: [],
  isLoading: false,
  error: null,
  currentStreamingMessageId: null,
  threadId: "",
  toolStatus: null,
  disfluencyMessage: null,
  widgetJson: null,
  userDetails: localStorage.getItem("user_details")
    ? JSON.parse(localStorage.getItem("user_details") || "{}")
    : null,

  // Rate limiting
  rateLimitStatus: {
    isRateLimited: false,
    limitType: null,
    message: null,
  },

  // Conversation management
  conversations: [],
  currentConversation: null,
  conversationsLoading: false,
};

export const useChatStore = create<ChatState>()((set, get) => ({
  ...initialState,

  // Actions

  logout: () => {
    localStorage.removeItem("user_details");
    localStorage.removeItem("jwt_token");
    set({ userDetails: null });

    // Reset chat state on logout
    set({
      messages: [],
      currentConversation: null,
      conversations: [],
      threadId: null,
    });
  },
  setUserDetails: (details) => {
    localStorage.setItem("user_details", details);
    const parsedDetails = JSON.parse(details);
    set({ userDetails: parsedDetails });
  },
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
      currentStreamingMessageId: message.isStreaming
        ? message.id
        : state.currentStreamingMessageId,
    })),

  updateToolMessage: (id, update) =>
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id && msg.role === "tool"
          ? {
              ...msg,
              toolStatus: update.toolStatus ?? msg.toolStatus,
              content: update.content ?? msg.content,
              endTime: update.endTime ?? msg.endTime,
            }
          : msg
      ),
    })),

  setWidgetJson: (json) => set({ widgetJson: json }),

  updateStreamingMessage: (id, update) =>
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id
          ? {
              ...msg,
              content: update.content ?? msg.content,
              json: update.json ?? msg.json,
            }
          : msg
      ),
    })),

  finishStreaming: (id) =>
    set((state) => ({
      messages: state.messages.map((msg) =>
        msg.id === id ? { ...msg, isStreaming: false } : msg
      ),
      currentStreamingMessageId: null,
    })),

  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  setThreadId: (threadId) => set({ threadId }),
  setToolStatus: (toolStatus) => set({ toolStatus }),
  setDisfluencyMessage: (message) => set({ disfluencyMessage: message }),

  // Rate limiting actions
  setRateLimitStatus: (status) => set({ rateLimitStatus: status }),

  clearRateLimitError: () =>
    set({
      rateLimitStatus: {
        isRateLimited: false,
        limitType: null,
        message: null,
      },
    }),

  checkRateLimitStatus: async (apiBaseUrl = "http://localhost:8000") => {
    try {
      const token = localStorage.getItem("jwt_token") || "";
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(`${apiBaseUrl}/api/rate-limit/status`, {
        method: "GET",
        headers,
      });

      if (!response.ok) {
        console.error("Failed to check rate limit status:", response.status);
        return;
      }

      const data = await response.json();

      // Check if rate limited
      if (
        data.limit_exceeded ||
        data.remaining_requests === 0 ||
        data.remaining_tokens === 0
      ) {
        set({
          rateLimitStatus: {
            isRateLimited: true,
            limitType: data.limit_type || "requests",
            message:
              data.limit_type === "tokens"
                ? `Daily token limit reached. Resets on ${data.reset_date}`
                : `Rate limit reached. Try again in ${Math.ceil(
                    (data.retry_after || 0) / 60
                  )} minutes.`,
            retryAfter: data.retry_after,
            remainingRequests: data.remaining_requests,
            remainingTokens: data.remaining_tokens,
            tokensUsed: data.tokens_used,
            dailyLimit: data.daily_limit,
            limit: data.limit,
            resetTime: data.reset_time,
            resetDate: data.reset_date,
          },
        });
      } else {
        // Not rate limited - update status
        set({
          rateLimitStatus: {
            isRateLimited: false,
            limitType: data.limit_type || null,
            message: null,
            remainingRequests: data.remaining_requests,
            remainingTokens: data.remaining_tokens,
            tokensUsed: data.tokens_used,
            dailyLimit: data.daily_limit,
            limit: data.limit,
            resetTime: data.reset_time,
            resetDate: data.reset_date,
          },
        });
      }

      console.log("📊 Rate limit status:", data);
    } catch (error) {
      console.error("Error checking rate limit status:", error);
    }
  },

  resetChat: () =>
    set({
      ...initialState,
      // Preserve conversations, user details, and rate limit status when resetting chat
      conversations: get().conversations,
      userDetails: get().userDetails,
      rateLimitStatus: get().rateLimitStatus,
      currentConversation: null,
    }),

  // Async Actions
  sendMessage: async (
    content: string,
    apiBaseUrl = "http://localhost:8000"
  ) => {
    if (!content.trim()) return;

    const store = get();

    const generateMessageId = (): string => {
      return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    };

    // Check if user is logged in using the helper
    const isLoggedIn = store.isLoggedIn();

    // Track if this is the first message in conversation (for logged-in users)
    const isFirstMessage =
      isLoggedIn && !store.currentConversation && store.messages.length === 0;

    // Add user message
    const userMessage = {
      id: generateMessageId(),
      role: "user" as const,
      content: content.trim(),
      timestamp: new Date(),
      json: undefined,
    };

    // Add initial assistant message
    const assistantMessageId = generateMessageId();
    const initialAssistantMessage = {
      id: assistantMessageId,
      role: "assistant" as const,
      content: "Just a moment",
      timestamp: new Date(),
      isStreaming: true,
      json: undefined,
    };

    // Set loading and clear error state before adding messages
    store.setLoading(true);
    store.setError(null);

    // Add messages to state
    store.addMessage(userMessage);
    store.addMessage(initialAssistantMessage);

    const assistantMessageCreated = true;

    try {
      const token = localStorage.getItem("jwt_token") || "";

      // Always send thread_id for LangGraph checkpointer (needed for context)
      // Backend will decide whether to persist to conversations table based on auth
      const response = await fetch(`${apiBaseUrl}/api/chat/stream`, {
        method: "POST",
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: content, thread_id: store.threadId }),
      });

      // Handle rate limiting (429) errors
      if (response.status === 429) {
        const errorData = await response.json();
        const detail = errorData.detail || errorData;

        // Set rate limit status
        store.setRateLimitStatus({
          isRateLimited: true,
          limitType: detail.limit_type || "requests",
          message: detail.message || detail.error || "Rate limit exceeded",
          retryAfter: detail.retry_after,
          remainingRequests: detail.remaining_requests,
          remainingTokens: detail.remaining_tokens,
          tokensUsed: detail.tokens_used,
          dailyLimit: detail.daily_limit,
          limit: detail.limit,
          resetTime: detail.reset_time,
          resetDate: detail.reset_date,
        });

        // Set error for UI
        store.setError(detail.message || detail.error || "Rate limit exceeded");
        store.setLoading(false);

        // Remove the placeholder assistant message
        if (assistantMessageCreated) {
          store.finishStreaming(assistantMessageId);
        }

        console.error("⛔ Rate limit exceeded:", detail);
        return;
      }

      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body reader available");

      const decoder = new TextDecoder();
      let accumulatedContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;

          const data = line.slice(6);
          if (data === "[DONE]") {
            store.finishStreaming(assistantMessageId);
            store.setLoading(false);
            store.setToolStatus(null);

            // For logged-in users: if this was the first message, fetch conversation and update URL
            if (isFirstMessage && isLoggedIn && store.threadId) {
              try {
                // Fetch the conversation by thread_id to get the conversation ID
                const token = localStorage.getItem("jwt_token") || "";
                const headers: HeadersInit = {
                  "Content-Type": "application/json",
                };
                if (token) {
                  headers["Authorization"] = `Bearer ${token}`;
                }

                // Get all conversations and find the one with matching thread_id
                const conversationsResponse = await fetch(
                  `${apiBaseUrl}/api/conversations`,
                  {
                    method: "GET",
                    headers,
                  }
                );

                if (conversationsResponse.ok) {
                  const conversationsData = await conversationsResponse.json();
                  const newConversation = conversationsData.conversations?.find(
                    (conv: Conversation) => conv.thread_id === store.threadId
                  );

                  if (newConversation) {
                    // Update current conversation
                    set({ currentConversation: newConversation });

                    // Update URL to include conversation ID
                    if (typeof window !== "undefined") {
                      window.history.pushState(
                        {},
                        "",
                        `/chat/c/${newConversation.id}`
                      );
                    }

                    // Refresh conversation list to show the new conversation
                    await store.loadConversations(apiBaseUrl);

                    console.log(
                      `✅ Created new conversation with ID: ${newConversation.id}`
                    );
                  }
                }
              } catch (error) {
                console.error(
                  "Failed to fetch conversation after creation:",
                  error
                );
                // Don't fail the entire flow, just log the error
              }
            }

            return;
          }

          try {
            const parsed = JSON.parse(data) as ChatChunkResponse;

            switch (parsed.event_name) {
              case "thread_info":
                console.log("🧠 Received thread_id:", parsed.thread_id);
                store.setThreadId(parsed.thread_id || "");
                break;

              case "llm_stream":
                if (parsed.text) {
                  const state = get();
                  const existingMessage = state.messages.find(
                    (msg) => msg.id === assistantMessageId
                  );

                  // If this is the first stream chunk and we have disfluency content,
                  // replace it entirely with the stream content
                  // Otherwise, append to existing content
                  const currentContent = existingMessage?.content || "";
                  const currentState = get();
                  const isDisfluencyContent =
                    currentState.disfluencyMessage &&
                    currentContent === currentState.disfluencyMessage;

                  let newContent: string;
                  if (isDisfluencyContent) {
                    // Replace disfluency with actual stream content
                    newContent = parsed.text;
                  } else {
                    // Append to existing content
                    newContent = currentContent + parsed.text;
                  }

                  store.updateStreamingMessage(assistantMessageId, {
                    content: newContent,
                  });
                }
                break;

              case "llm_json_complete":
                if (parsed.json) {
                  store.updateStreamingMessage(assistantMessageId, {
                    json: parsed.json,
                  });
                }
                break;

              case "error_message":
                if (parsed.text) {
                  console.error("Workflow error:", parsed.text);
                  store.setError(parsed.text);
                }
                break;

              case "workflow_json":
                if (parsed.json) {
                  store.setWidgetJson(parsed.json);
                  // Also attach widget to the current assistant message
                  store.updateStreamingMessage(assistantMessageId, {
                    json: parsed.json,
                  });
                  emitter.emit(EVENT_EMITTER_ADD_WORKFLOW_JSON, parsed.json);
                }
                break;

              case "widget_event":
                if (parsed.widget_type && parsed.payload) {
                  const widgetData = {
                    template: parsed.widget_type,
                    payload: parsed.payload,
                  };
                  store.setWidgetJson(widgetData);
                  // Also attach widget to the current assistant message
                  store.updateStreamingMessage(assistantMessageId, {
                    json: widgetData,
                  });
                  emitter.emit(EVENT_EMITTER_ADD_WORKFLOW_JSON, widgetData);
                }
                break;

              case "workflow_widget_json":
                // Legacy support - will be removed after migration
                if (
                  parsed.json &&
                  parsed.json.template &&
                  parsed.json.payload
                ) {
                  const templatePayload = parsed.json;
                  store.setWidgetJson(
                    templatePayload ?? { template: "", payload: {} }
                  );
                  // Also attach widget to the current assistant message
                  if (templatePayload) {
                    store.updateStreamingMessage(assistantMessageId, {
                      json: templatePayload,
                    });
                    emitter.emit(
                      EVENT_EMITTER_ADD_WORKFLOW_JSON,
                      templatePayload
                    );
                  }
                }
                break;

              case "disfluency_generated":
                if (parsed.text) {
                  // Replace the initial "Just a moment..." message with disfluency
                  store.updateStreamingMessage(assistantMessageId, {
                    content: parsed.text,
                  });
                  store.setDisfluencyMessage(parsed.text);
                }
                break;

              case "error":
                console.error("Backend error:", parsed.error);
                store.setError(parsed.error || "");
                if (parsed.thread_id) store.setThreadId(parsed.thread_id);
                break;

              default:
                if (parsed.text) {
                  const state = get();
                  const existingMessage = state.messages.find(
                    (msg) => msg.id === assistantMessageId
                  );

                  // Handle disfluency replacement for default case as well
                  const currentContent = existingMessage?.content || "";
                  const currentState = get();
                  const isDisfluencyContent =
                    currentState.disfluencyMessage &&
                    currentContent === currentState.disfluencyMessage;

                  let newContent: string;
                  if (isDisfluencyContent) {
                    // Replace disfluency with actual stream content
                    accumulatedContent = parsed.text;
                    newContent = parsed.text;
                  } else {
                    // Append to existing content
                    accumulatedContent += parsed.text;
                    newContent = accumulatedContent;
                  }

                  store.updateStreamingMessage(assistantMessageId, {
                    content: newContent,
                    json: parsed.json,
                  });
                }
                break;
            }
          } catch {
            continue; // Skip invalid JSON
          }
        }
      }

      if (assistantMessageCreated) {
        store.finishStreaming(assistantMessageId);
      }
      store.setLoading(false);
    } catch (error) {
      console.error("Error sending message:", error);
      store.setError(
        error instanceof Error ? error.message : "An error occurred"
      );
      store.setLoading(false);
      store.setToolStatus(null);

      if (assistantMessageCreated) {
        store.finishStreaming(assistantMessageId);
      }
    }
  },

  loadConversationHistory: async (
    threadId: string,
    apiBaseUrl = "http://localhost:8000"
  ) => {
    const store = get();
    const generateMessageId = (): string => {
      return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    };

    try {
      // TODO: This endpoint doesn't exist yet - we need to create it
      // It should retrieve messages from LangGraph checkpointer using thread_id
      const response = await fetch(
        `${apiBaseUrl}/api/chat/history/${threadId}`
      );

      if (!response.ok) {
        // If history endpoint doesn't exist, just reset chat without messages
        if (response.status === 404) {
          console.log(
            `📚 No history found for thread ${threadId}, starting fresh`
          );
          store.setThreadId(threadId);
          store.resetChat();
          return;
        }
        throw new Error(
          `Failed to load conversation history: ${response.status}`
        );
      }

      const data = await response.json();
      const messages = (data.messages || []).map(
        (msg: {
          role: "user" | "assistant";
          content: string;
          timestamp?: string;
          widget_json?: { template: string; payload: unknown };
        }) => ({
          id: generateMessageId(),
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
          widget_json: msg.widget_json,
        })
      );

      store.setThreadId(threadId);
      store.resetChat();
      messages.forEach(store.addMessage);
      const lastMessage = messages[messages.length - 1];
      if (lastMessage.widget_json) {
        store.setWidgetJson({
          template: getDetails(lastMessage, "widget_json.widget_type") || "",
          payload: getDetails(lastMessage, "widget_json.payload") || {},
        });
      }

      console.log(
        `📚 Loaded ${messages.length} messages from thread ${threadId}`
      );
    } catch (error) {
      console.error("Error loading conversation history:", error);
      // Don't show error to user if it's just missing history
      if (error instanceof Error && !error.message.includes("404")) {
        store.setError(`Failed to load conversation history: ${error.message}`);
      }
      // Still set the thread ID so new messages work
      store.setThreadId(threadId);
      store.resetChat();
    }
  },

  // ============================================================================
  // CONVERSATION MANAGEMENT FUNCTIONS
  // ============================================================================
  // These functions interact with the cleaned up conversation API endpoints:
  // - GET /api/conversations - List user conversations
  // - GET /api/conversations/id/{id} - Get specific conversation by ID
  // - PUT /api/conversations/id/{id} - Update conversation metadata
  // - DELETE /api/conversations/id/{id} - Delete conversation permanently
  //
  // All functions use consistent error handling and logging patterns.
  // ============================================================================

  loadConversations: async (apiBaseUrl = "http://localhost:8000") => {
    set({ conversationsLoading: true });

    try {
      const token = localStorage.getItem("jwt_token");
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(`${apiBaseUrl}/api/conversations`, {
        method: "GET",
        headers,
      });

      if (!response.ok) {
        throw new Error(
          `Failed to load conversations: ${response.status} ${response.statusText}`
        );
      }

      const data = await response.json();
      set({
        conversations: data.conversations || [],
        conversationsLoading: false,
      });

      console.log(`📚 Loaded ${data.conversations?.length || 0} conversations`);
    } catch (error) {
      console.error("Error loading conversations:", error);
      set({
        error: `Failed to load conversations: ${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        conversationsLoading: false,
        conversations: [], // Reset to empty array on error
      });
    }
  },

  createNewConversation: async () => {
    const store = get();

    // Generate new thread ID
    const newThreadId = `chat_${Date.now()}_${Math.random()
      .toString(36)
      .substr(2, 9)}`;

    // Reset chat state for new conversation
    store.resetChat();
    store.setThreadId(newThreadId);

    // Don't navigate here - let the router handle URL changes
    // The URL should already be correct (/chat or /chat/new)

    // The conversation will be created automatically when the first message is sent
    return newThreadId;
  },

  loadConversationById: async (
    conversationId: number,
    apiBaseUrl = "http://localhost:8000"
  ) => {
    try {
      const token = localStorage.getItem("jwt_token");
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(
        `${apiBaseUrl}/api/conversations/id/${conversationId}`,
        {
          method: "GET",
          headers,
        }
      );

      if (!response.ok) {
        throw new Error(
          `Failed to load conversation: ${response.status} ${response.statusText}`
        );
      }

      const conversation: Conversation = await response.json();

      // Load the conversation history
      await get().loadConversationHistory(conversation.thread_id, apiBaseUrl);

      // Set as current conversation
      set((state) => ({
        ...state,
        currentConversation: conversation,
        threadId: conversation.thread_id,
      }));

      // Don't update URL here - let the router handle it
      // The URL should already be correct since we're loading based on the URL

      console.log(
        `✅ Loaded conversation: ${conversation.title || conversation.id}`
      );
    } catch (error) {
      console.error("Failed to load conversation by ID:", error);
      get().setError(
        `Failed to load conversation: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
      throw error;
    }
  },

  switchConversation: async (
    threadId: string,
    apiBaseUrl = "http://localhost:8000"
  ) => {
    const store = get();

    try {
      // Find the conversation in the loaded conversations
      const conversation = store.conversations.find(
        (conv) => conv.thread_id === threadId
      );

      if (conversation) {
        set({ currentConversation: conversation });

        // Update URL
        if (typeof window !== "undefined" && conversation.id) {
          window.history.pushState({}, "", `/chat/c/${conversation.id}`);
        }
      }

      // Load conversation history
      await store.loadConversationHistory(threadId, apiBaseUrl);

      console.log(`🔄 Switched to conversation: ${threadId}`);
    } catch (error) {
      console.error("Error switching conversation:", error);
      store.setError(
        `Failed to switch conversation: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    }
  },

  switchConversationById: async (
    conversationId: number,
    apiBaseUrl = "http://localhost:8000"
  ) => {
    const store = get();

    try {
      // Find the conversation in the loaded conversations
      const conversation = store.conversations.find(
        (conv) => conv.id === conversationId
      );

      if (conversation) {
        set({ currentConversation: conversation });

        // Load conversation history
        await store.loadConversationHistory(conversation.thread_id, apiBaseUrl);

        // Update URL
        if (typeof window !== "undefined") {
          window.history.pushState({}, "", `/chat/c/${conversationId}`);
        }

        console.log(`🔄 Switched to conversation ID: ${conversationId}`);
      } else {
        // If not found in loaded conversations, try to load it directly
        // But don't update the URL again to prevent loops
        const token = localStorage.getItem("jwt_token");
        const headers: HeadersInit = {
          "Content-Type": "application/json",
        };

        if (token) {
          headers["Authorization"] = `Bearer ${token}`;
        }

        const response = await fetch(
          `${apiBaseUrl}/api/conversations/id/${conversationId}`,
          {
            method: "GET",
            headers,
          }
        );

        if (!response.ok) {
          throw new Error(
            `Failed to load conversation: ${response.status} ${response.statusText}`
          );
        }

        const conversation: Conversation = await response.json();

        // Load the conversation history
        await store.loadConversationHistory(conversation.thread_id, apiBaseUrl);

        // Set as current conversation
        set((state) => ({
          ...state,
          currentConversation: conversation,
          threadId: conversation.thread_id,
        }));

        console.log(
          `✅ Loaded conversation: ${conversation.title || conversation.id}`
        );
      }
    } catch (error) {
      console.error("Error switching conversation by ID:", error);
      store.setError(
        `Failed to switch conversation: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    }
  },

  updateConversationTitle: async (
    conversationId: number,
    title: string,
    apiBaseUrl = "http://localhost:8000"
  ) => {
    const store = get();

    try {
      const token = localStorage.getItem("jwt_token");
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(
        `${apiBaseUrl}/api/conversations/id/${conversationId}`,
        {
          method: "PUT",
          headers,
          body: JSON.stringify({ title }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Failed to update conversation title: ${response.status} ${response.statusText} - ${errorText}`
        );
      }

      const updatedConversation = await response.json();

      // Update conversations list
      const updatedConversations = store.conversations.map((conv) =>
        conv.id === conversationId ? updatedConversation : conv
      );

      set({
        conversations: updatedConversations,
        currentConversation:
          store.currentConversation?.id === conversationId
            ? updatedConversation
            : store.currentConversation,
      });

      console.log(
        `✏️ Updated conversation title: "${title}" (ID: ${conversationId})`
      );
    } catch (error) {
      console.error("Error updating conversation title:", error);
      store.setError(
        `Failed to update conversation title: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
      throw error; // Re-throw so UI can handle it
    }
  },

  deleteConversation: async (
    conversationId: number,
    apiBaseUrl = "http://localhost:8000"
  ) => {
    const store = get();

    try {
      const token = localStorage.getItem("jwt_token");
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      const response = await fetch(
        `${apiBaseUrl}/api/conversations/id/${conversationId}`,
        {
          method: "DELETE",
          headers,
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Failed to delete conversation: ${response.status} ${response.statusText} - ${errorText}`
        );
      }

      // Remove from conversations list
      const updatedConversations = store.conversations.filter(
        (conv) => conv.id !== conversationId
      );

      set({ conversations: updatedConversations });

      // If this was the current conversation, reset chat and navigate to new chat
      if (store.currentConversation?.id === conversationId) {
        store.resetChat();
        set({ currentConversation: null });

        // Navigate to new chat
        if (typeof window !== "undefined") {
          window.history.pushState({}, "", "/chat");
        }
      }

      console.log(`🗑️ Deleted conversation (ID: ${conversationId})`);
    } catch (error) {
      console.error("Error deleting conversation:", error);
      store.setError(
        `Failed to delete conversation: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
      throw error; // Re-throw so UI can handle it
    }
  },

  // Selectors
  getToolMessageById: (id) =>
    get().messages.find((msg) => msg.role === "tool" && msg.id === id),

  getToolMessages: () => get().messages.filter((msg) => msg.role === "tool"),

  getChatMessages: () =>
    get().messages.filter(
      (msg) => msg.role === "user" || msg.role === "assistant"
    ),

  getActiveToolMessages: () =>
    get().messages.filter(
      (msg) =>
        msg.role === "tool" &&
        (msg.toolStatus === "started" || msg.toolStatus === "in_progress")
    ),

  getCompletedToolMessages: () =>
    get().messages.filter(
      (msg) =>
        msg.role === "tool" &&
        (msg.toolStatus === "completed" || msg.toolStatus === "failed")
    ),

  // Auth helper - checks both JWT token and user details for reliability
  isLoggedIn: () => {
    const token = localStorage.getItem("jwt_token");
    const userDetails = get().userDetails;
    // User is logged in if both token exists AND userDetails exists
    return !!(token && userDetails);
  },
}));

// Sync function to check localStorage and update store if out of sync
const syncAuthState = () => {
  const store = useChatStore.getState();
  const token = localStorage.getItem("jwt_token");
  const userDetailsStr = localStorage.getItem("user_details");

  // If no token but store has userDetails, logout
  if (!token && store.userDetails) {
    console.log("🔓 JWT token missing - logging out");
    store.logout();
    return;
  }

  // If no userDetails but store has them, logout
  if (!userDetailsStr && store.userDetails) {
    console.log("🔓 User details missing - logging out");
    store.logout();
    return;
  }

  // If localStorage has userDetails but store doesn't, login
  if (userDetailsStr && !store.userDetails) {
    console.log("🔐 User details found - syncing login state");
    try {
      store.setUserDetails(userDetailsStr);
    } catch (error) {
      console.error("Failed to sync user details:", error);
    }
  }
};

// Listen for localStorage changes from OTHER tabs
if (typeof window !== "undefined") {
  window.addEventListener("storage", (event) => {
    // Only handle auth-related keys
    if (event.key === "jwt_token" || event.key === "user_details") {
      console.log(`🔄 Storage changed in another tab: ${event.key}`);
      syncAuthState();
    }
  });

  // Check localStorage when tab becomes visible (handles same-tab DevTools changes)
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) {
      console.log("👁️ Tab visible - checking auth state");
      syncAuthState();
    }
  });

  // Also check on window focus (backup for visibility change)
  window.addEventListener("focus", () => {
    console.log("🎯 Window focused - checking auth state");
    syncAuthState();
  });
}

// Export the store hook for easy access
