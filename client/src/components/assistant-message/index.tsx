import { LuBrainCircuit, LuThumbsDown, LuThumbsUp } from "react-icons/lu";
import type { Message } from "../../types/chat";

type AssistantMessageProps = {
  message: Message;
};

const AssistantMessage = ({ message }: AssistantMessageProps) => {
  return (
    <div className="flex flex-col w-full mb-8 gap-2">
      <div className="w-full flex flex-col gap-6 bg-[#151718] rounded-2xl px-8 pt-8 pb-16 relative">
        <div className="w-15 h-15 rounded-2xl absolute -bottom-7 flex justify-center items-center left-8 bg-blue-500 text-white">
          <LuBrainCircuit className="w-10 h-10" />
        </div>
        <div className="w-full text-base text-white">{message.content}</div>
      </div>

      {/* actions */}

      <div className="flex w-full justify-between">
        <span />

        <div className="flex items-center gap-2">
          <button
            className="bg-[#151718] rounded-lg px-2 py-1 hover:bg-black transition-all duration-300 active:bg-neutral-900 active:scale-95 group"
            onClick={() => {
              navigator.clipboard.writeText(message.content);
            }}
          >
            <span className="text-gray-400 text-xs font-medium group-hover:text-white transition-all duration-300">
              Copy
            </span>
          </button>

          <button className="bg-[#151718] rounded-lg px-3 py-1 hover:bg-black transition-all duration-300 active:bg-neutral-900 active:scale-95 group">
            <span className="text-gray-400 text-xs font-medium group-hover:text-white transition-all duration-300">
              Regenerate Response
            </span>
          </button>

          <div className="bg-[#151718] rounded-lg px-3 py-1 flex items-center justify-center gap-2">
            <LuThumbsUp className="w-4 h-4 text-gray-400 hover:text-white transition-all duration-300" />
            <LuThumbsDown className="w-4 h-4 text-gray-400 hover:text-white transition-all duration-300" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssistantMessage;
