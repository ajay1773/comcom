import { useState } from "react";
import { LuUser, LuCheck, LuCopy } from "react-icons/lu";
import type { Message } from "../../types/chat";
import { useChatStore } from "@/store/chat-store";

type UserMessageProps = {
  message: Message;
};

const UserMessage = ({ message }: UserMessageProps) => {
  const { userDetails } = useChatStore();
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
      <div className="w-full flex flex-col gap-2 bg-neutral-500/10 rounded-xl sm:rounded-2xl px-3 sm:px-5 md:px-8 pt-4 sm:pt-6 md:pt-8 pb-10 sm:pb-12 md:pb-16 relative">
        <div className="w-10 h-10 sm:w-12 sm:h-12 md:w-15 md:h-15 rounded-xl sm:rounded-2xl flex justify-center items-center absolute -bottom-5 sm:-bottom-6 md:-bottom-7 right-3 sm:right-5 md:right-8 bg-primary text-primary-foreground font-bold text-base sm:text-xl md:text-2xl">
          {userDetails ? (
            userDetails?.first_name?.[0] + userDetails?.last_name?.[0]
          ) : (
            <LuUser className="w-5 h-5 sm:w-7 sm:h-7 md:w-10 md:h-10" />
          )}
        </div>
        <div className="w-full text-sm sm:text-base text-white leading-relaxed">
          {message.content}
        </div>
      </div>

      {/* Copy button */}
      <div className="flex w-full justify-start">
        <button
          className="bg-neutral-500/10 rounded-lg px-2.5 sm:px-3 py-1.5 sm:py-2 hover:bg-neutral-500/20 transition-all duration-300 active:bg-neutral-500/30 active:scale-95 group flex items-center gap-1.5 sm:gap-2"
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

export default UserMessage;
