import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import clsx from "clsx";
import {
  LuMessageSquare,
  LuStar,
  LuArchive,
  LuTrash2,
  LuPenLine,
  LuEllipsisVertical,
  LuCheck,
  LuX,
} from "react-icons/lu";
import { useChatStore, type Conversation } from "../../store/chat-store";

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onSelect: (conversationId: number) => void;
  onEdit: (conversationId: number, title: string) => void;
  onArchive: (conversationId: number, archived: boolean) => void;
  onFavorite: (conversationId: number, favorite: boolean) => void;
  onDelete: (conversationId: number) => void;
}

const ConversationItem: React.FC<ConversationItemProps> = ({
  conversation,
  isActive,
  onSelect,
  onEdit,
  onArchive,
  onFavorite,
  onDelete,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(conversation.title || "");
  const [showMenu, setShowMenu] = useState(false);

  const handleEdit = () => {
    if (isEditing && conversation.id) {
      onEdit(conversation.id, editTitle);
      setIsEditing(false);
    } else {
      setEditTitle(conversation.title || "");
      setIsEditing(true);
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(conversation.title || "");
    setIsEditing(false);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return "Today";
    if (diffDays === 2) return "Yesterday";
    if (diffDays <= 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <div
      className={clsx(
        "group relative p-3 rounded-lg cursor-pointer transition-all duration-200",
        {
          "bg-blue-500/20 border border-blue-500/30": isActive,
          "hover:bg-neutral-700/30": !isActive,
        }
      )}
    >
      <div className="flex items-start justify-between">
        <div
          className="flex-1 min-w-0"
          onClick={() =>
            !isEditing && conversation.id && onSelect(conversation.id)
          }
        >
          <div className="flex items-center gap-2 mb-1">
            <LuMessageSquare className="w-4 h-4 text-neutral-400 flex-shrink-0" />
            {conversation.is_favorite && (
              <LuStar className="w-3 h-3 text-yellow-500 fill-current" />
            )}
            {conversation.is_archived && (
              <LuArchive className="w-3 h-3 text-neutral-500" />
            )}
          </div>

          {isEditing ? (
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                className="flex-1 bg-neutral-800 text-white text-sm px-2 py-1 rounded border border-neutral-600 focus:border-blue-500 focus:outline-none"
                placeholder="Conversation title"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleEdit();
                  if (e.key === "Escape") handleCancelEdit();
                }}
              />
              <button
                onClick={handleEdit}
                className="p-1 text-green-500 hover:text-green-400"
              >
                <LuCheck className="w-3 h-3" />
              </button>
              <button
                onClick={handleCancelEdit}
                className="p-1 text-red-500 hover:text-red-400"
              >
                <LuX className="w-3 h-3" />
              </button>
            </div>
          ) : (
            <>
              <h3 className="text-sm font-medium text-white truncate">
                {conversation.title || "New Chat"}
              </h3>
              <div className="flex items-center justify-between mt-1">
                <p className="text-xs text-neutral-400">
                  {conversation.message_count} messages
                </p>
                <p className="text-xs text-neutral-500">
                  {formatDate(conversation.last_message_at)}
                </p>
              </div>
            </>
          )}
        </div>

        {!isEditing && (
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              className="p-1 text-neutral-400 hover:text-white opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <LuEllipsisVertical className="w-4 h-4" />
            </button>

            {showMenu && (
              <div className="absolute right-0 top-6 bg-neutral-800 border border-neutral-700 rounded-lg shadow-lg z-10 min-w-[150px]">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsEditing(true);
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-white hover:bg-neutral-700 flex items-center gap-2"
                >
                  <LuPenLine className="w-3 h-3" />
                  Rename
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (conversation.id) {
                      onFavorite(conversation.id, !conversation.is_favorite);
                    }
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-white hover:bg-neutral-700 flex items-center gap-2"
                >
                  <LuStar className="w-3 h-3" />
                  {conversation.is_favorite ? "Unfavorite" : "Favorite"}
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (conversation.id) {
                      onArchive(conversation.id, !conversation.is_archived);
                    }
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-white hover:bg-neutral-700 flex items-center gap-2"
                >
                  <LuArchive className="w-3 h-3" />
                  {conversation.is_archived ? "Unarchive" : "Archive"}
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    if (
                      window.confirm(
                        "Are you sure you want to delete this conversation?"
                      )
                    ) {
                      if (conversation.id) {
                        onDelete(conversation.id);
                      }
                    }
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-2 text-left text-sm text-red-400 hover:bg-neutral-700 flex items-center gap-2"
                >
                  <LuTrash2 className="w-3 h-3" />
                  Delete
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Click outside to close menu */}
      {showMenu && (
        <div className="fixed inset-0 z-5" onClick={() => setShowMenu(false)} />
      )}
    </div>
  );
};

interface ConversationListProps {
  className?: string;
}

const ConversationList: React.FC<ConversationListProps> = ({ className }) => {
  const navigate = useNavigate();
  const {
    conversations,
    conversationsLoading,
    currentConversation,
    loadConversations,
    updateConversationTitle,
    archiveConversation,
    favoriteConversation,
    deleteConversation,
  } = useChatStore();

  useEffect(() => {
    // Load conversations when component mounts
    loadConversations();
  }, [loadConversations]);

  const filteredConversations = conversations.filter((conv) => {
    // Show all non-archived conversations by default
    return !conv.is_archived;
  });

  const handleConversationSelect = async (conversationId: number) => {
    // Use React Router navigation instead of direct store call
    navigate(`/chat/c/${conversationId}`);
  };

  if (conversationsLoading) {
    return (
      <div className={clsx("flex items-center justify-center p-4", className)}>
        <div className="text-neutral-400 text-sm">Loading conversations...</div>
      </div>
    );
  }

  return (
    <div className={clsx("flex flex-col h-full", className)}>
      {/* Conversations list */}
      <div className="flex-1 overflow-y-auto space-y-2">
        {filteredConversations.length === 0 ? (
          <div className="text-center text-neutral-400 text-sm py-8">
            No conversations yet
          </div>
        ) : (
          filteredConversations.map((conversation) => (
            <ConversationItem
              key={conversation.id || conversation.thread_id}
              conversation={conversation}
              isActive={
                currentConversation?.id === conversation.id ||
                (currentConversation?.thread_id === conversation.thread_id &&
                  !conversation.id)
              }
              onSelect={handleConversationSelect}
              onEdit={updateConversationTitle}
              onArchive={archiveConversation}
              onFavorite={favoriteConversation}
              onDelete={deleteConversation}
            />
          ))
        )}
      </div>
    </div>
  );
};

export default ConversationList;
