import Sidebar from "../../components/sidebar";
import ChatWindow from "../../components/chat-window";

const Chat = () => {
  return (
    <div className="flex w-full h-full">
      <Sidebar />
      <ChatWindow />
    </div>
  );
};

export default Chat;
