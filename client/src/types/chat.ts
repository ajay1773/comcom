/**
 * ChatChunkResponse models the payload sent via Server-Sent Events (SSE)
 * from the backend. Each message contains an `event_name` that determines
 * how the client should interpret the rest of the payload.
 *
 * Common events:
 * - "thread_info": carries the server-assigned thread_id
 * - "disfluency_generated": short, friendly status message while processing
 * - "llm_stream": incremental natural-language tokens from the model
 * - "llm_json_complete": a complete JSON object (not chunked)
 * - "workflow_progress": progress updates for long-running workflows
 * - "workflow_completed": a workflow has finished running
 * - "workflow_text": final human-readable text response
 * - "workflow_json": final structured JSON response
 * - "error_message": user-friendly error message
 */
export type ChatChunkResponse = {
  /** Name of the event emitted by the server */
  event_name: string;
  /** Human-readable text (used by multiple events, e.g., workflow_text) */
  text?: string;
  /** Thread identifier for chat continuity */
  thread_id?: string;
  /** Raw error string (when present) */
  error?: string;
  /** Structured JSON payload (final or complete objects only) */
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
};

export type ToolStatus = "started" | "in_progress" | "completed" | "failed";
