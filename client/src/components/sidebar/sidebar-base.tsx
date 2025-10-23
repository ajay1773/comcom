import { useState, useEffect } from "react";
import {
  LuBrainCircuit,
  LuPlus,
  LuSearch,
  LuUser,
  LuTrash2,
  LuLogOut,
} from "react-icons/lu";
import { useChatStore } from "../../store/chat-store";
import { Button } from "../ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

interface SidebarBaseProps {
  onConversationClick?: () => void; // Callback to close mobile sidebar
}

const SidebarBase = ({ onConversationClick }: SidebarBaseProps) => {
  const {
    conversations,
    currentConversation,
    switchConversationById,
    createNewConversation,
    conversationsLoading,
    loadConversations,
    logout,
    userDetails,
    deleteConversation,
  } = useChatStore();

  const [searchQuery, setSearchQuery] = useState("");
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const handleNewChat = async () => {
    await createNewConversation();
    onConversationClick?.();
  };

  const handleConversationClick = async (conversationId: number) => {
    await switchConversationById(conversationId);
    onConversationClick?.();
  };

  const handleDeleteClick = (conversationId: number, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent conversation selection
    setDeleteConfirmId(conversationId);
  };

  const handleDeleteConfirm = async () => {
    if (deleteConfirmId) {
      try {
        await deleteConversation(deleteConfirmId);
        setDeleteConfirmId(null);
      } catch (error) {
        console.error("Failed to delete conversation:", error);
        // Error is already handled in the store
      }
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirmId(null);
  };

  // Filter conversations based on search query
  const filteredConversations = conversations.filter((conv) =>
    conv.title?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex flex-col h-full">
      {/* Header with Logo */}
      <div className="flex items-center gap-2 p-3 border-b border-neutral-700/30 h-[56px] lg:h-[68px]">
        <LuBrainCircuit className="text-blue-500 size-6 flex-shrink-0" />
        <span className="text-lg font-semibold text-foreground whitespace-nowrap">
          ComCom
        </span>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <Button
          onClick={handleNewChat}
          className="w-full justify-start gap-2 bg-blue-600 hover:bg-blue-700"
        >
          <LuPlus className="size-4 flex-shrink-0" />
          <span>New chat</span>
        </Button>
      </div>

      {/* Search */}
      <div className="px-3 pb-3">
        <div className="relative">
          <LuSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 size-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 bg-neutral-800/50 border border-neutral-700/30 rounded-md text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto px-2 py-3">
        {conversationsLoading ? (
          <div className="text-center text-muted-foreground text-sm p-4">
            Loading...
          </div>
        ) : filteredConversations.length === 0 ? (
          <div className="text-center text-muted-foreground text-sm p-4">
            No conversations
          </div>
        ) : (
          <div className="space-y-1">
            {filteredConversations.map((conv) => (
              <div key={conv.id} className="relative group">
                {deleteConfirmId === conv.id ? (
                  // Confirmation dialog
                  <div className="bg-red-900/20 border border-red-500/30 rounded-md p-3 space-y-2">
                    <p className="text-xs text-red-400">
                      Delete this conversation?
                    </p>
                    <div className="flex gap-2">
                      <button
                        onClick={handleDeleteConfirm}
                        className="flex-1 px-2 py-1 bg-red-600 hover:bg-red-700 text-white text-xs rounded transition-colors"
                      >
                        Delete
                      </button>
                      <button
                        onClick={handleDeleteCancel}
                        className="flex-1 px-2 py-1 bg-neutral-600 hover:bg-neutral-700 text-white text-xs rounded transition-colors"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  // Normal conversation item
                  <button
                    onClick={() => handleConversationClick(conv.id)}
                    className={cn(
                      "w-full text-left px-3 py-2 rounded-md text-sm transition-colors group relative",
                      currentConversation?.id === conv.id
                        ? "bg-neutral-700/50 text-foreground"
                        : "text-muted-foreground hover:bg-neutral-800/50 hover:text-foreground"
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <div className="truncate flex-1 pr-2">
                        {conv.title || "New Conversation"}
                      </div>
                      <button
                        onClick={(e) => handleDeleteClick(conv.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-600/20 rounded transition-all duration-200 flex-shrink-0"
                        title="Delete conversation"
                      >
                        <LuTrash2 className="size-3 text-red-400 hover:text-red-300" />
                      </button>
                    </div>
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Bottom Section - User Profile */}
      <div className="border-t border-neutral-700/30">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="w-full flex items-center gap-3 px-3 py-3 text-sm text-muted-foreground hover:bg-neutral-800/50 hover:text-foreground transition-colors">
              <div className="size-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                {userDetails?.first_name?.[0]?.toUpperCase() || (
                  <LuUser className="size-4" />
                )}
              </div>
              <div className="flex-1 text-left truncate">
                <div className="font-medium text-foreground truncate">
                  {userDetails?.first_name} {userDetails?.last_name}
                </div>
                <div className="text-xs truncate">{userDetails?.email}</div>
              </div>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent
            className="w-56 mx-3"
            side="top"
            align="center"
            sideOffset={8}
          >
            <DropdownMenuLabel className="font-normal">
              <div className="flex flex-col space-y-1">
                <p className="text-sm font-medium leading-none">
                  {userDetails?.first_name} {userDetails?.last_name}
                </p>
                <p className="text-xs leading-none text-muted-foreground">
                  {userDetails?.email}
                </p>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              onClick={logout}
              className="text-red-400 focus:text-red-400"
            >
              <LuLogOut className="mr-2 h-4 w-4" />
              <span>Logout</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
};

export default SidebarBase;
