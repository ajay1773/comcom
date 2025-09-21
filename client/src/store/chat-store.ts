import { create } from "zustand";
import type { ChatChunkResponse, Message, ToolStatus } from "../types/chat";
import { EVENT_EMITTER_ADD_WORKFLOW_JSON } from "@/config";
import emitter from "@/core/event-emitter";
import { extractTemplatePayload } from "@/utils/extraction";

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  currentStreamingMessageId: string | null;
  threadId: string | null;
  toolStatus: ToolStatus | null;
  disfluencyMessage: string | null;
  widgetJson: { template: string; payload: unknown } | null;

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

  // Async Actions
  sendMessage: (content: string, apiBaseUrl?: string) => Promise<void>;
  loadConversationHistory: (
    threadId: string,
    apiBaseUrl?: string
  ) => Promise<void>;

  // Selectors
  getToolMessageById: (id: string) => Message | undefined;
  getActiveToolMessages: () => Message[];
  getCompletedToolMessages: () => Message[];
  getToolMessages: () => Message[];
  getChatMessages: () => Message[];
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
};

export const useChatStore = create<ChatState>()((set, get) => ({
  ...initialState,

  // Actions
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

  resetChat: () => set(initialState),

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
      const response = await fetch(`${apiBaseUrl}/api/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("jwt_token") || ""}`,
        },
        body: JSON.stringify({ query: content, thread_id: store.threadId }),
      });

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
                  emitter.emit(EVENT_EMITTER_ADD_WORKFLOW_JSON, parsed.json);
                }
                break;

              case "workflow_widget_json":
                if (parsed.json) {
                  const templatePayload = extractTemplatePayload(
                    JSON.stringify(parsed.json)
                  );
                  store.setWidgetJson(
                    templatePayload ?? { template: "", payload: {} }
                  );
                  if (templatePayload) {
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
      const response = await fetch(
        `${apiBaseUrl}/api/chat/history/${threadId}`
      );
      if (!response.ok) {
        throw new Error(
          `Failed to load conversation history: ${response.status}`
        );
      }

      const data = await response.json();
      const messages = data.messages.map(
        (msg: {
          role: "user" | "assistant";
          content: string;
          timestamp?: string;
        }) => ({
          id: generateMessageId(),
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
        })
      );

      store.setThreadId(threadId);
      store.resetChat();
      messages.forEach(store.addMessage);

      console.log(
        `📚 Loaded ${messages.length} messages from thread ${threadId}`
      );
    } catch (error) {
      console.error("Error loading conversation history:", error);
      store.setError(
        `Failed to load conversation history: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
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
}));

// Export the store hook for easy access
export const useChat = () => {
  return useChatStore();
};
