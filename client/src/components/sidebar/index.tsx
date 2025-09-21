import clsx from "clsx";
import { useState } from "react";
import {
  LuBrainCircuit,
  LuCalendarCheck,
  LuChevronUp,
  LuColumns2,
  LuMessageSquareText,
  LuPlus,
  LuScanBarcode,
  LuSearch,
  LuSettings,
  LuRotateCcw,
} from "react-icons/lu";
import { useChat } from "../../store/chat-store";

const navItems: {
  icon: React.ReactNode;
  title: string;
  link: string;
}[] = [
  {
    icon: <LuMessageSquareText className="text-blue-500 size-5" />,
    title: "Chats",
    link: "/chats",
  },
  {
    icon: <LuSearch className="text-green-500 size-5" />,
    title: "Search",
    link: "/search",
  },
  {
    icon: <LuCalendarCheck className="text-purple-500 size-5" />,
    title: "Manage Subscription",
    link: "/manage-subscription",
  },
  {
    icon: <LuScanBarcode className="text-orange-500 size-5" />,
    title: "Updates and FAQ",
    link: "/updates-and-faq",
  },
  {
    icon: <LuSettings className="text-purple-500 size-5" />,
    title: "Settings",
    link: "/settings",
  },
];

const chatListItems: {
  icon: React.ReactNode;
  title: string;
  link: string;
}[] = [
  {
    icon: <span className="bg-blue-500 size-5 rounded" />,
    title: "Favourites",
    link: "/favourites",
  },
  {
    icon: <span className="bg-amber-600 size-5 rounded" />,
    title: "Archived",
    link: "/archived",
  },
];

const Sidebar = () => {
  const { resetChat } = useChat();
  const [active, setActive] = useState<(typeof navItems)[0]>(navItems[0]);
  const [chatListActive, setChatListActive] = useState<
    (typeof chatListItems)[0]
  >(chatListItems[0]);
  const [chatListOpen, setChatListOpen] = useState(true);

  const handleNewChat = () => {
    resetChat();
  };

  const handleResetChat = () => {
    if (
      window.confirm(
        "Are you sure you want to reset the current chat? This action cannot be undone."
      )
    ) {
      resetChat();
    }
  };
  return (
    <div className="bg-transparent w-1/5 h-full">
      <div className="flex flex-col w-full h-full justify-between py-4">
        <div className="flex flex-col w-full gap-10">
          <div className="flex w-full justify-between items-center px-6">
            <div className="flex gap-2 items-center">
              <LuBrainCircuit className="text-blue-500 size-[40px]" />
              <p className="text-2xl font-bold">Brainwave</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleResetChat}
                className="flex justify-center items-center hover:bg-neutral-600/10 rounded-lg p-1 active:scale-95 transition-all duration-300 cursor-pointer group"
                title="Reset Chat"
              >
                <LuRotateCcw className="text-neutral-400 group-hover:text-white size-[18px] transition-all duration-300" />
              </button>
              <LuColumns2 className="text-neutral-400 size-[22px]" />
            </div>
          </div>

          <div className="flex flex-col w-full px-6">
            {navItems.map((item) => (
              <button
                className={clsx(
                  "w-full px-6 py-4 rounded-lg flex items-center justify-start gap-4 hover:bg-neutral-600/10 transition-all duration-300 cursor-pointer",
                  {
                    "bg-neutral-600/20 shadow-md": active.link === item.link,
                  }
                )}
                onClick={() => setActive(item)}
              >
                {item.icon}
                <p
                  className={clsx(
                    "text-gray-400 text-md font-medium transition-all duration-300",
                    {
                      "text-white": active.link === item.link,
                    }
                  )}
                >
                  {item.title}
                </p>
              </button>
            ))}
          </div>

          <hr className="w-full border-neutral-800 h-[1px]" />

          <div className="flex flex-col w-full px-6">
            <button
              className="flex w-full justify-start items-center gap-4 ml-6 group cursor-pointer mb-4"
              onClick={() => setChatListOpen(!chatListOpen)}
            >
              <LuChevronUp
                className={clsx(
                  "text-neutral-700 size-[20px] group-hover:text-neutral-500 transition-all duration-300",
                  {
                    "rotate-180": chatListOpen,
                  }
                )}
              />
              <span className="text-neutral-700 text-sm font-medium group-hover:text-neutral-500 transition-all duration-300">
                Chat List
              </span>
            </button>

            <div
              className={clsx(
                "flex flex-col w-full transition-all duration-300",
                {
                  hidden: !chatListOpen,
                }
              )}
            >
              {chatListItems.map((item) => (
                <button
                  className={clsx(
                    "w-full px-6 py-4 rounded-lg flex items-center justify-start gap-4 hover:bg-neutral-600/10 transition-all duration-300 cursor-pointer",
                    {
                      "bg-neutral-600/20 shadow-md":
                        chatListActive.link === item.link,
                    }
                  )}
                  onClick={() => setChatListActive(item)}
                >
                  {item.icon}
                  <p
                    className={clsx(
                      "text-gray-400 text-md font-medium transition-all duration-300",
                      {
                        "text-white": chatListActive.link === item.link,
                      }
                    )}
                  >
                    {item.title}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-6 px-6">
          <button
            onClick={handleNewChat}
            className="w-full px-6 py-4 rounded-lg bg-blue-500 flex items-center justify-center gap-2 active:scale-95 hover:bg-blue-600 transition-all duration-300 cursor-pointer"
          >
            <LuPlus className="text-white size-[20px]" />
            <span className="text-white text-md font-semibold">New Chat</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
