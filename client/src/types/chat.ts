/**
 * ChatChunkResponse models the payload sent via Server-Sent Events (SSE)
 * from the backend. Each message contains an `event_name` that determines
 * how the client should interpret the rest of the payload.
 *
 * Common events:
 * - "thread_info": carries the server-assigned thread_id
 * - "disfluency_generated": short, friendly status message while processing
 * - "llm_stream": incremental natural-language tokens from the model
 * - "widget_event": structured UI widget data with specific type
 * - "workflow_widget_json": legacy widget format (deprecated)
 * - "error_message": user-friendly error message
 */
export type ChatChunkResponse = {
  /** Name of the event emitted by the server */
  event_name: string;
  /** Human-readable text (used by multiple events, e.g., llm_stream) */
  text?: string;
  /** Thread identifier for chat continuity */
  thread_id?: string;
  /** Raw error string (when present) */
  error?: string;
  /** Widget type for widget_event */
  widget_type?: string;
  /** Widget payload for widget_event */
  payload?: unknown;
  /** Legacy structured JSON payload (deprecated) */
  json?: {
    template: string;
    payload: unknown;
  };
};

export type Message = {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  toolType?: "search" | "calculation" | "other";
  toolStatus?: ToolStatus;
  toolQuery?: string;
  startTime?: Date;
  endTime?: Date;
  json?: {
    template: string;
    payload: unknown;
  };
  widget_json?: {
    template: string;
    payload: unknown;
  };
};

export type ToolStatus = "started" | "in_progress" | "completed" | "failed";
