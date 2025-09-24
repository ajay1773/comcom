import { LuUser } from "react-icons/lu";
import type { Message } from "../../types/chat";
import { useChatStore } from "@/store/chat-store";

type UserMessageProps = {
  message: Message;
};

const UserMessage = ({ message }: UserMessageProps) => {
  const { userDetails } = useChatStore();
  return (
    <div className="w-full flex flex-col gap-2 bg-neutral-500/10 rounded-2xl px-8 pt-8 pb-16 relative mb-8">
      {/* <img
        src={USER_IMAGE}
        alt="user"
        className="w-15 h-15 rounded-2xl absolute -bottom-7 right-8"
      /> */}
      <div className="w-15 h-15 rounded-2xl flex justify-center items-center absolute -bottom-7 right-8 bg-primary text-primary-foreground font-bold text-2xl">
        {userDetails ? (
          userDetails?.first_name?.[0] + userDetails?.last_name?.[0]
        ) : (
          <LuUser className="w-10 h-10" />
        )}
      </div>
      <div className="w-full text-base text-white">{message.content}</div>
    </div>
  );
};

export default UserMessage;
