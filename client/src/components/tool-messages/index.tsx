import { useChat } from "../../store/chat-store";
import type { Message } from "../../types/chat";

interface ToolMessageCardProps {
  message: Message;
}

const ToolMessageCard: React.FC<ToolMessageCardProps> = ({ message }) => {
  const getStatusIcon = (status: Message["toolStatus"]) => {
    switch (status) {
      case "started":
        return "🔄";
      case "in_progress":
        return "⏳";
      case "completed":
        return "✅";
      case "failed":
        return "❌";
      default:
        return "❓";
    }
  };

  const getStatusColor = (status: Message["toolStatus"]) => {
    switch (status) {
      case "started":
      case "in_progress":
        return "text-blue-600 bg-blue-50";
      case "completed":
        return "text-green-600 bg-green-50";
      case "failed":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getTypeIcon = (type: Message["toolType"]) => {
    switch (type) {
      case "search":
        return "🔍";
      case "calculation":
        return "🧮";
      default:
        return "🛠️";
    }
  };

  const duration =
    message.startTime && message.endTime
      ? message.endTime.getTime() - message.startTime.getTime()
      : null;

  return (
    <div
      className={`p-3 rounded-lg border-l-4 ${getStatusColor(
        message.toolStatus
      )} border-l-current mb-2`}
    >
      <div className="flex items-center gap-2 mb-1">
        <span className="text-lg">{getTypeIcon(message.toolType)}</span>
        <span className="text-lg">{getStatusIcon(message.toolStatus)}</span>
        <span className="font-medium text-sm capitalize">
          {message.toolType} Tool
        </span>
        {duration && (
          <span className="text-xs text-gray-500 ml-auto">
            {Math.round(duration / 1000)}s
          </span>
        )}
      </div>

      <div className="text-sm">
        {message.toolQuery && (
          <div className="mb-1">
            <strong>Query:</strong>{" "}
            <code className="bg-gray-100 px-1 rounded">
              {message.toolQuery}
            </code>
          </div>
        )}
        <div>{message.content}</div>
      </div>

      <div className="text-xs text-gray-500 mt-1">
        {message.timestamp.toLocaleTimeString()}
      </div>
    </div>
  );
};

export const ToolMessages: React.FC = () => {
  const { getActiveToolMessages, getCompletedToolMessages } = useChat();

  const activeTools = getActiveToolMessages();
  const completedTools = getCompletedToolMessages();

  if (activeTools.length === 0 && completedTools.length === 0) {
    return null;
  }

  return (
    <div className="tool-messages">
      {/* Active Tool Messages */}
      {activeTools.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">
            🔄 Active Tools
          </h4>
          {activeTools.map((tool) => (
            <ToolMessageCard key={tool.id} message={tool} />
          ))}
        </div>
      )}

      {/* Completed Tool Messages */}
      {completedTools.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-2">
            ✅ Completed Tools
          </h4>
          {completedTools.map((tool) => (
            <ToolMessageCard key={tool.id} message={tool} />
          ))}
        </div>
      )}
    </div>
  );
};

// New component for showing all messages in chronological order
export const ChatMessagesWithTools: React.FC = () => {
  const { state } = useChat();

  return (
    <div className="chat-messages">
      {state.messages.map((message) => {
        if (message.role === "tool") {
          return <ToolMessageCard key={message.id} message={message} />;
        }

        // Regular chat message
        return (
          <div
            key={message.id}
            className={`mb-4 ${
              message.role === "user" ? "text-right" : "text-left"
            }`}
          >
            <div
              className={`inline-block p-3 rounded-lg max-w-xs lg:max-w-md ${
                message.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 text-gray-900"
              }`}
            >
              {message.content}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ToolMessages;
