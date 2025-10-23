import { useState } from "react";
import { LuBrainCircuit, LuCheck, LuCopy } from "react-icons/lu";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { Message } from "../../types/chat";

type AssistantMessageProps = {
  message: Message;
  widgetComponent?: React.ReactNode;
};

const AssistantMessage = ({
  message,
  widgetComponent,
}: AssistantMessageProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text:", err);
    }
  };

  return (
    <div className="flex flex-col w-full mb-6 sm:mb-7 md:mb-8 gap-2">
      <div className="w-full flex flex-col gap-4 sm:gap-5 md:gap-6 bg-[#151718] rounded-xl sm:rounded-2xl px-3 sm:px-5 md:px-8 pt-4 sm:pt-6 md:pt-8 pb-10 sm:pb-12 md:pb-16 relative">
        <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-15 md:h-15 rounded-xl sm:rounded-2xl absolute -bottom-5 sm:-bottom-6 md:-bottom-7 flex justify-center items-center left-3 sm:left-5 md:left-8 bg-blue-500 text-white">
          <LuBrainCircuit className="w-5 h-5 sm:w-7 sm:h-7 md:w-10 md:h-10" />
        </div>
        <div className="w-full text-sm sm:text-base text-white leading-relaxed prose prose-invert prose-sm sm:prose-base max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Widget Component - displayed inside the message on mobile/tablet only */}
        {widgetComponent && (
          <div className="w-full mt-2 sm:mt-3 md:mt-4 lg:hidden">
            {widgetComponent}
          </div>
        )}
      </div>

      {/* Copy button with feedback */}
      <div className="flex w-full justify-end">
        <button
          className="bg-[#151718] rounded-lg px-2.5 sm:px-3 py-1.5 sm:py-2 hover:bg-black transition-all duration-300 active:bg-neutral-900 active:scale-95 group flex items-center gap-1.5 sm:gap-2"
          onClick={handleCopy}
        >
          {copied ? (
            <>
              <LuCheck className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-green-400" />
              <span className="text-green-400 text-[10px] sm:text-xs font-medium">
                Copied!
              </span>
            </>
          ) : (
            <>
              <LuCopy className="w-3 h-3 sm:w-3.5 sm:h-3.5 text-gray-400 group-hover:text-white transition-all duration-300" />
              <span className="text-gray-400 text-[10px] sm:text-xs font-medium group-hover:text-white transition-all duration-300">
                Copy
              </span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default AssistantMessage;
