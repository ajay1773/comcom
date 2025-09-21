import { useRef, useState } from "react";
import { LuCirclePlus, LuSend } from "react-icons/lu";

type AutoResizeInputProps = {
  placeholder?: string;
  onSubmit?: (message: string) => void;
  onMessageChange?: (message: string) => void;
  disabled?: boolean;
  className?: string;
};

const AutoResizeInput = ({
  placeholder = "Type your message here...",
  onSubmit,
  onMessageChange,
  disabled = false,
  className = "",
}: AutoResizeInputProps) => {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = e.target;
    const newMessage = textarea.value;
    setMessage(newMessage);

    // Reset height to auto to get the correct scrollHeight
    textarea.style.height = "auto";

    // Set the height to match the scroll height, but respect max-height
    const maxHeight = 120; // ~6 lines of text
    const newHeight = Math.min(textarea.scrollHeight, maxHeight);
    textarea.style.height = `${newHeight}px`;

    // Call optional callback
    onMessageChange?.(newMessage);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSubmit?.(message.trim());
      setMessage("");
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  return (
    <div
      className={`flex flex-col border border-neutral-600 rounded-lg p-4 gap-4 ${className}`}
    >
      <textarea
        ref={textareaRef}
        value={message}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        rows={1}
        disabled={disabled}
        className="w-full resize-none bg-transparent border-none outline-none text-white placeholder-neutral-400 leading-5 disabled:opacity-50 disabled:cursor-not-allowed overflow-y-auto"
        placeholder={placeholder}
        style={{
          minHeight: "20px",
          maxHeight: "120px", // ~6 lines of text
        }}
      />

      <div className="flex w-full justify-between items-center">
        <button
          onClick={handleSubmit}
          disabled={disabled || !message.trim()}
          className="flex justify-center items-center hover:bg-neutral-600/10 rounded-lg p-2 active:scale-95 transition-all duration-300 cursor-pointer group"
        >
          <LuCirclePlus className="text-neutral-400 size-[20px]" />{" "}
        </button>

        <button
          onClick={handleSubmit}
          disabled={disabled || !message.trim()}
          className="flex-shrink-0 p-2 rounded-lg bg-blue-500 flex justify-center items-center transition-colors duration-200 hover:bg-blue-600 hover:text-neutral-300 disabled:opacity-50 disabled:cursor-not-allowed mt-0.5"
        >
          <LuSend className="text-white size-[20px]" />
        </button>
      </div>
    </div>
  );
};

export default AutoResizeInput;
