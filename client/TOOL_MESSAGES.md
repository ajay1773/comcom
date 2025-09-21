# Tool Messages System

## Overview

The enhanced chat context now provides a scalable way to handle tool calls (like web search, calculations, etc.) as structured messages that maintain chronological order with regular chat messages.

## Key Features

### 🎯 **Unified Message Stream**

- Tool messages are stored in the main messages array alongside chat messages
- Maintains chronological order of all conversation events
- Easy to display in timeline format or filter by type

### 🔄 **Lifecycle Management**

- **Started**: Tool begins execution
- **In Progress**: Tool is actively running (extensible)
- **Completed**: Tool finished successfully
- **Failed**: Tool encountered an error

### 🧩 **Scalable Design**

- Supports multiple tool types: `search`, `calculation`, `other`
- Easy to extend for new tools
- Structured data with query extraction

### ⏱️ **Performance Tracking**

- Start/end timestamps
- Duration calculation
- Status transitions

## Data Structure

```typescript
interface Message {
  id: string;
  role: "user" | "assistant" | "tool";
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  // Tool-specific properties (only for role="tool")
  toolType?: "search" | "calculation" | "other";
  toolStatus?: "started" | "in_progress" | "completed" | "failed";
  toolQuery?: string; // For search tools
  startTime?: Date;
  endTime?: Date;
}
```

## Usage Examples

### Basic Usage

```tsx
import { useChat } from "../contexts/chat-context";

function ChatComponent() {
  const { state, getChatMessages, getActiveToolMessages } = useChat();

  return (
    <div>
      {/* All messages in chronological order */}
      {state.messages.map((msg) => {
        if (msg.role === "tool") {
          return <ToolCard key={msg.id} tool={msg} />;
        }
        return <ChatMessage key={msg.id} message={msg} />;
      })}

      {/* Or separate chat messages */}
      {getChatMessages().map((msg) => (
        <ChatMessage key={msg.id} message={msg} />
      ))}
    </div>
  );
}
```

### Tool Status Indicator

```tsx
function ToolStatusIndicator() {
  const { getActiveToolMessages } = useChat();
  const activeTools = getActiveToolMessages();

  if (activeTools.length === 0) return null;

  return (
    <div className="tool-indicator">
      {activeTools.map((tool) => (
        <div key={tool.id} className="animate-pulse">
          🔄 {tool.type} running...
        </div>
      ))}
    </div>
  );
}
```

### Tool History Panel

```tsx
function ToolHistory() {
  const { getCompletedToolMessages } = useChat();
  const completedTools = getCompletedToolMessages();

  return (
    <div className="tool-history">
      <h3>Tool History</h3>
      {completedTools.map((tool) => {
        const duration =
          tool.endTime && tool.startTime
            ? tool.endTime.getTime() - tool.startTime.getTime()
            : 0;

        return (
          <div key={tool.id}>
            <span>{tool.toolType}</span>
            <span>{tool.toolQuery}</span>
            <span>{Math.round(duration / 1000)}s</span>
          </div>
        );
      })}
    </div>
  );
}
```

## Backend Integration

The system automatically handles backend tool status messages:

```json
// Tool started
{
  "tool_message": "🔍 Searching internet for \"weather Delhi\"...",
  "type": "tool_status",
  "status": "started"
}

// Tool completed
{
  "tool_message": "✅ Search completed, generating response...",
  "type": "tool_status",
  "status": "completed"
}
```

## Extending for New Tools

### Adding a New Tool Type

1. **Update the type union**:

```typescript
toolType?: "search" | "calculation" | "api_call" | "other";
```

2. **Update the parser**:

```typescript
const parseToolMessage = (message: string) => {
  if (message.includes("🧮 Calculating")) {
    return { type: "calculation" as const };
  }
  if (message.includes("📡 Calling API")) {
    return { type: "api_call" as const };
  }
  // ... existing logic
};
```

3. **Update UI components**:

```typescript
const getTypeIcon = (type: Message["toolType"]) => {
  switch (type) {
    case "search":
      return "🔍";
    case "calculation":
      return "🧮";
    case "api_call":
      return "📡";
    default:
      return "🛠️";
  }
};
```

## Context API Methods

### State Access

- `state.messages` - All messages (chat + tool messages in chronological order)
- `state.toolStatus` - Current tool status (for indicators)

### Helper Methods

- `getToolMessageById(id)` - Find specific tool message
- `getToolMessages()` - Get all tool messages
- `getChatMessages()` - Get only user/assistant messages
- `getActiveToolMessages()` - Get running tools
- `getCompletedToolMessages()` - Get finished tools

## Best Practices

### 1. **Chronological vs Separated Display**

```tsx
// ✅ Chronological: Show everything in order
{state.messages.map(msg =>
  msg.role === "tool" ? <ToolCard key={msg.id} tool={msg} /> : <ChatMessage key={msg.id} message={msg} />
)}

// ✅ Separated: Show tools and chat separately
<ChatMessages messages={getChatMessages()} />
<ToolMessages />

// ✅ Both approaches are valid depending on UX needs
```

### 2. **Progressive Enhancement**

```tsx
// Show basic status, expand for details
<ToolCard tool={tool} showDetails={expandedTools.includes(tool.id)} />
```

### 3. **Performance Monitoring**

```tsx
// Use duration for performance insights
const slowTools = getCompletedToolMessages().filter(
  (t) =>
    t.endTime &&
    t.startTime &&
    t.endTime.getTime() - t.startTime.getTime() > 5000
);
```

### 4. **Error Handling**

```tsx
const failedTools = getToolMessages().filter((t) => t.toolStatus === "failed");
if (failedTools.length > 0) {
  // Show retry options or error details
}
```

## Migration from Old System

### Old System Issues

- Tool messages were separate from chat flow
- Lost chronological ordering
- Harder to build timeline UIs

### New Unified System

```tsx
// ✅ All messages in chronological order
state.messages; // Contains user, assistant, and tool messages

// ✅ Easy filtering when needed
getChatMessages(); // Only user/assistant
getToolMessages(); // Only tool messages
getActiveToolMessages(); // Only running tools

// ✅ Timeline display
{
  state.messages.map((msg) => {
    switch (msg.role) {
      case "user":
        return <UserMessage key={msg.id} message={msg} />;
      case "assistant":
        return <AIMessage key={msg.id} message={msg} />;
      case "tool":
        return <ToolMessage key={msg.id} message={msg} />;
    }
  });
}
```

### Key Benefits

- **Chronological Order**: Tools appear exactly when they were executed
- **Unified State**: Single array to manage, simpler state logic
- **Flexible Display**: Can show timeline or filtered views
- **Better UX**: Users see tool activity in context of conversation

This provides better user experience with natural conversation flow including tool usage!
