import clsx from "clsx";
import { useState } from "react";
import {
  LuBrainCircuit,
  LuChevronDown,
  LuColumns2,
  LuMessageSquareText,
  LuPlus,
  LuSettings,
  LuRotateCcw,
  LuUser,
  LuCircle,
} from "react-icons/lu";
import { useChatStore } from "../../store/chat-store";
import ConversationList from "../conversation-list";

// Accordion Section Interface
interface AccordionSection {
  id: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  isOpen: boolean;
  content: React.ReactNode;
}

const Sidebar = () => {
  const { resetChat, createNewConversation } = useChatStore();

  // State for accordion sections
  const [accordionSections, setAccordionSections] = useState<
    AccordionSection[]
  >([
    {
      id: "conversations",
      title: "Conversations",
      icon: LuMessageSquareText,
      isOpen: true,
      content: <ConversationList className="flex-1" />,
    },
    {
      id: "settings",
      title: "Settings",
      icon: LuSettings,
      isOpen: false,
      content: (
        <div className="px-4 py-2 space-y-2">
          <button className="w-full text-left text-sm text-neutral-400 hover:text-white transition-colors py-1">
            Theme
          </button>
          <button className="w-full text-left text-sm text-neutral-400 hover:text-white transition-colors py-1">
            Notifications
          </button>
          <button className="w-full text-left text-sm text-neutral-400 hover:text-white transition-colors py-1">
            Privacy
          </button>
        </div>
      ),
    },
    {
      id: "profile",
      title: "Profile",
      icon: LuUser,
      isOpen: false,
      content: (
        <div className="px-4 py-2 space-y-2">
          <button className="w-full text-left text-sm text-neutral-400 hover:text-white transition-colors py-1">
            Account Info
          </button>
          <button className="w-full text-left text-sm text-neutral-400 hover:text-white transition-colors py-1">
            Preferences
          </button>
        </div>
      ),
    },
    {
      id: "help",
      title: "Help & Support",
      icon: LuCircle,
      isOpen: false,
      content: (
        <div className="px-4 py-2 space-y-2">
          <button className="w-full text-left text-sm text-neutral-400 hover:text-white transition-colors py-1">
            Documentation
          </button>
          <button className="w-full text-left text-sm text-neutral-400 hover:text-white transition-colors py-1">
            Contact Support
          </button>
          <button className="w-full text-left text-sm text-neutral-400 hover:text-white transition-colors py-1">
            Feedback
          </button>
        </div>
      ),
    },
  ]);

  const handleNewChat = async () => {
    await createNewConversation();
    // Navigation is handled in the createNewConversation function
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

  const toggleAccordionSection = (sectionId: string) => {
    setAccordionSections((prev) =>
      prev.map((section) =>
        section.id === sectionId
          ? { ...section, isOpen: !section.isOpen }
          : section
      )
    );
  };
  return (
    <div className="bg-transparent w-1/5 h-full">
      <div className="flex flex-col w-full h-full justify-between py-4">
        <div className="flex flex-col w-full gap-6">
          {/* Header */}
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

          {/* Accordion Sections */}
          <div className="flex flex-col w-full px-6 flex-1 min-h-0 space-y-2">
            {accordionSections.map((section) => {
              const IconComponent = section.icon;
              return (
                <div
                  key={section.id}
                  className="border border-neutral-800 rounded-lg overflow-hidden"
                >
                  {/* Accordion Header */}
                  <button
                    className="flex w-full justify-between items-center p-4 hover:bg-neutral-800/30 transition-all duration-200 group"
                    onClick={() => toggleAccordionSection(section.id)}
                    aria-expanded={section.isOpen}
                    aria-controls={`accordion-content-${section.id}`}
                  >
                    <div className="flex items-center gap-3">
                      <IconComponent className="text-neutral-400 group-hover:text-white size-[18px] transition-colors duration-200" />
                      <span className="text-neutral-300 text-sm font-medium group-hover:text-white transition-colors duration-200">
                        {section.title}
                      </span>
                    </div>
                    <LuChevronDown
                      className={clsx(
                        "text-neutral-400 group-hover:text-white size-[16px] transition-all duration-200",
                        {
                          "rotate-180": section.isOpen,
                        }
                      )}
                    />
                  </button>

                  {/* Accordion Content */}
                  <div
                    id={`accordion-content-${section.id}`}
                    className={clsx(
                      "overflow-hidden transition-all duration-300 ease-in-out",
                      {
                        "max-h-0": !section.isOpen,
                        "max-h-96":
                          section.isOpen && section.id !== "conversations",
                        "max-h-full":
                          section.isOpen && section.id === "conversations",
                      }
                    )}
                  >
                    <div className="border-t border-neutral-800">
                      {section.id === "conversations" ? (
                        <div className="p-2 max-h-64 overflow-y-auto">
                          {section.content}
                        </div>
                      ) : (
                        <div className="pb-2">{section.content}</div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
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
