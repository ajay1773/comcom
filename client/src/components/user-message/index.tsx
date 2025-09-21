import { USER_IMAGE } from "../../config";
import type { Message } from "../../types/chat";

type UserMessageProps = {
  message: Message;
};

const UserMessage = ({ message }: UserMessageProps) => {
  return (
    <div className="w-full flex flex-col gap-2 bg-neutral-500/10 rounded-2xl px-8 pt-8 pb-16 relative mb-8">
      <img
        src={USER_IMAGE}
        alt="user"
        className="w-15 h-15 rounded-2xl absolute -bottom-7 right-8"
      />
      <div className="w-full text-base text-white">{message.content}</div>
    </div>
  );
};

export default UserMessage;
