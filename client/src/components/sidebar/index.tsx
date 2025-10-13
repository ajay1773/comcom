import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  LuBrainCircuit,
  LuColumns2,
  LuMessageSquareText,
  LuPlus,
  LuRotateCcw,
  LuSearch,
  LuStar,
  LuArchive,
  LuClock,
  LuHeart,
} from "react-icons/lu";
import { useChatStore } from "../../store/chat-store";
import ConversationList from "../conversation-list";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/accordion";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandShortcut,
} from "@/components/ui/command";

// Chat Section Interface
interface ChatSection {
  id: string;
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  count?: number;
}

const Sidebar = () => {
  const navigate = useNavigate();
  const { resetChat, createNewConversation, conversations, loadConversations } =
    useChatStore();

  // State for search command dialog
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  // Chat sections data
  const chatSections: ChatSection[] = [
    {
      id: "all",
      title: "All",
      icon: LuMessageSquareText,
      count: 12,
    },
    {
      id: "favorites",
      title: "Favorites",
      icon: LuStar,
      count: 3,
    },
    {
      id: "archived",
      title: "Archived",
      icon: LuArchive,
      count: 8,
    },
  ];

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

  const handleSearchChats = () => {
    setIsSearchOpen(true);
  };

  const handleSelectConversation = async (conversationId: number) => {
    try {
      // Use React Router navigation instead of direct store call
      navigate(`/chat/${conversationId}`);
      setIsSearchOpen(false);
    } catch (error) {
      console.error("Failed to switch conversation:", error);
    }
  };

  const formatRelativeTime = (dateString: string | null) => {
    if (!dateString) return "Unknown";

    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) return "Just now";
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400)
      return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800)
      return `${Math.floor(diffInSeconds / 86400)}d ago`;

    return date.toLocaleDateString();
  };

  // Filter conversations for search
  const recentConversations = conversations
    .filter((conv) => !conv.is_archived)
    .sort(
      (a, b) =>
        new Date(b.last_message_at || b.created_at || "").getTime() -
        new Date(a.last_message_at || a.created_at || "").getTime()
    )
    .slice(0, 10);

  const favoriteConversations = conversations.filter(
    (conv) => conv.is_favorite && !conv.is_archived
  );
  const archivedConversations = conversations.filter(
    (conv) => conv.is_archived
  );

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Handle keyboard shortcuts for search dialog
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Cmd+L or Ctrl+L to open search
      if (event.key === "l" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        setIsSearchOpen(true);
      }
      // Cmd+N or Ctrl+N to create new chat
      if (event.key === "n" && (event.metaKey || event.ctrlKey)) {
        event.preventDefault();
        handleNewChat();
      }
      // Escape to close search
      if (event.key === "Escape" && isSearchOpen) {
        setIsSearchOpen(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [isSearchOpen]);
  return (
    <div className="bg-transparent w-1/5 h-full">
      <div className="flex flex-col w-full h-full py-4">
        {/* Header */}
        <div className="flex w-full justify-between items-center px-6 mb-6">
          <div className="flex gap-2 items-center">
            <LuBrainCircuit className="text-blue-500 size-[40px]" />
            <p className="text-2xl font-bold">ComCom</p>
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

        {/* Action Buttons */}
        <div className="flex flex-col gap-3 px-6 mb-6">
          {/* New Chat Button */}
          <button
            onClick={handleNewChat}
            className="w-full px-4 py-3 rounded-lg hover:bg-neutral-800/30 flex items-center gap-3 transition-all duration-200 text-left"
          >
            <LuPlus className="text-neutral-400 size-[18px]" />
            <span className="text-neutral-300 text-sm font-medium">
              New chat
            </span>
          </button>

          {/* Search Chats Button */}
          <button
            onClick={handleSearchChats}
            className="w-full px-4 py-3 rounded-lg hover:bg-neutral-800/30 flex items-center gap-3 transition-all duration-200 text-left group"
          >
            <LuSearch className="text-neutral-400 size-[18px]" />
            <span className="text-neutral-300 text-sm font-medium flex-1">
              Search chats
            </span>
            <kbd className="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-neutral-800 px-1.5 font-mono text-[10px] font-medium text-neutral-400 opacity-100 group-hover:bg-neutral-700">
              <span className="text-xs">⌘</span>L
            </kbd>
          </button>
        </div>

        {/* Chat Sections */}
        <div className="flex flex-col w-full px-6 flex-1 min-h-0">
          <Accordion type="multiple" defaultValue={["all"]} className="w-full">
            {chatSections.map((section) => {
              return (
                <AccordionItem
                  key={section.id}
                  value={section.id}
                  className="border-none"
                >
                  <AccordionTrigger className="py-2 px-2 hover:bg-neutral-800/20 rounded transition-all duration-200 hover:no-underline [&[data-state=open]>svg]:rotate-180">
                    <div className="flex items-center gap-2">
                      <span className="text-neutral-500 text-sm font-normal">
                        {section.title}
                      </span>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="ml-4 pb-1 pt-0">
                    {section.id === "all" && (
                      <div className="max-h-64 overflow-y-auto">
                        <ConversationList className="flex-1" />
                      </div>
                    )}
                    {section.id === "favorites" && (
                      <div className="px-2 py-2 text-neutral-500 text-sm">
                        No favorite chats yet
                      </div>
                    )}
                    {section.id === "archived" && (
                      <div className="px-2 py-2 text-neutral-500 text-sm">
                        No archived chats
                      </div>
                    )}
                  </AccordionContent>
                </AccordionItem>
              );
            })}
          </Accordion>
        </div>

        {/* User Profile at Bottom */}
        <div className="px-6 pt-4 border-t border-neutral-800">
          <div className="flex items-center gap-3 p-2 hover:bg-neutral-800/20 rounded transition-all duration-200 cursor-pointer">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-semibold">AK</span>
            </div>
            <div className="flex-1">
              <p className="text-neutral-300 text-sm font-medium">Ajay Kumar</p>
              <p className="text-neutral-500 text-xs">Free</p>
            </div>
          </div>
        </div>

        {/* Search Command Dialog */}
        <CommandDialog
          open={isSearchOpen}
          onOpenChange={setIsSearchOpen}
          title="Search Conversations"
          description="Find and navigate to your conversations"
        >
          <CommandInput placeholder="Search conversations..." />
          <CommandList>
            <CommandEmpty>No conversations found.</CommandEmpty>

            {recentConversations.length > 0 && (
              <CommandGroup heading="Recent Conversations">
                {recentConversations.map((conversation) => (
                  <CommandItem
                    key={conversation.id}
                    value={`${conversation.title} ${conversation.id}`}
                    onSelect={() => handleSelectConversation(conversation.id)}
                    className="flex items-center gap-3 py-3"
                  >
                    <LuMessageSquareText className="size-4 text-neutral-400" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-neutral-200 truncate">
                        {conversation.title || "Untitled Chat"}
                      </div>
                      <div className="text-xs text-neutral-500 flex items-center gap-2">
                        <LuClock className="size-3" />
                        {formatRelativeTime(conversation.last_message_at)}
                        {conversation.message_count > 0 && (
                          <span>• {conversation.message_count} messages</span>
                        )}
                      </div>
                    </div>
                    {conversation.is_favorite && (
                      <LuHeart className="size-4 text-red-500 fill-red-500" />
                    )}
                  </CommandItem>
                ))}
              </CommandGroup>
            )}

            {favoriteConversations.length > 0 && (
              <CommandGroup heading="Favorites">
                {favoriteConversations.map((conversation) => (
                  <CommandItem
                    key={`fav-${conversation.id}`}
                    value={`favorite ${conversation.title} ${conversation.id}`}
                    onSelect={() => handleSelectConversation(conversation.id)}
                    className="flex items-center gap-3 py-3"
                  >
                    <LuHeart className="size-4 text-red-500 fill-red-500" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-neutral-200 truncate">
                        {conversation.title || "Untitled Chat"}
                      </div>
                      <div className="text-xs text-neutral-500 flex items-center gap-2">
                        <LuClock className="size-3" />
                        {formatRelativeTime(conversation.last_message_at)}
                      </div>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}

            {archivedConversations.length > 0 && (
              <CommandGroup heading="Archived">
                {archivedConversations.slice(0, 5).map((conversation) => (
                  <CommandItem
                    key={`arch-${conversation.id}`}
                    value={`archived ${conversation.title} ${conversation.id}`}
                    onSelect={() => handleSelectConversation(conversation.id)}
                    className="flex items-center gap-3 py-3"
                  >
                    <LuArchive className="size-4 text-neutral-400" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-neutral-200 truncate">
                        {conversation.title || "Untitled Chat"}
                      </div>
                      <div className="text-xs text-neutral-500 flex items-center gap-2">
                        <LuClock className="size-3" />
                        {formatRelativeTime(conversation.last_message_at)}
                      </div>
                    </div>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}

            <CommandGroup heading="Actions">
              <CommandItem
                value="new chat"
                onSelect={() => {
                  handleNewChat();
                  setIsSearchOpen(false);
                }}
                className="flex items-center gap-3 py-3"
              >
                <LuPlus className="size-4 text-neutral-400" />
                <span className="text-sm">New Chat</span>
                <CommandShortcut>⌘N</CommandShortcut>
              </CommandItem>
            </CommandGroup>
          </CommandList>
        </CommandDialog>
      </div>
    </div>
  );
};

export default Sidebar;
