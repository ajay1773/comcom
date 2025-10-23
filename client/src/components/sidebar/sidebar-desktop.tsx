import { useState } from "react";
import {
  LuChevronLeft,
  LuChevronRight,
  LuPlus,
  LuUser,
  LuLogOut,
} from "react-icons/lu";
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
import SidebarBase from "./sidebar-base";
import { useChatStore } from "../../store/chat-store";

interface SidebarDesktopProps {
  defaultExpanded?: boolean;
}

const SidebarDesktop = ({ defaultExpanded = true }: SidebarDesktopProps) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const { createNewConversation, userDetails, logout } = useChatStore();

  const handleNewChat = async () => {
    await createNewConversation();
  };

  return (
    <div
      className={cn(
        "relative h-full bg-neutral-900/50 border-r border-neutral-700/30 flex transition-all duration-300 ease-in-out",
        isExpanded ? "w-64" : "w-16"
      )}
    >
      {/* Collapse/Expand Button - Positioned absolutely over the sidebar */}
      <div className="absolute top-5 right-3 z-10">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsExpanded(!isExpanded)}
          className="size-8 flex-shrink-0 hover:bg-neutral-700/50"
        >
          {isExpanded ? (
            <LuChevronLeft className="size-4" />
          ) : (
            <LuChevronRight className="size-4" />
          )}
        </Button>
      </div>

      {/* Sidebar Content */}
      <div
        className={cn(
          "w-full transition-opacity duration-300",
          !isExpanded && "opacity-0 pointer-events-none"
        )}
      >
        {isExpanded && <SidebarBase />}
      </div>

      {/* Collapsed State - Show minimal indicators */}
      {!isExpanded && (
        <div className="w-full flex flex-col items-center pt-16 px-2 gap-3">
          {/* New Chat Button */}
          <button
            onClick={handleNewChat}
            className="size-10 rounded-lg bg-blue-600 hover:bg-blue-700 flex items-center justify-center transition-colors group"
            title="New chat"
          >
            <LuPlus className="size-5 text-white" />
          </button>

          {/* User Avatar with Menu */}
          <div className="mt-auto mb-4">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  className="size-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center hover:scale-105 transition-transform"
                  title={`${userDetails?.first_name} ${userDetails?.last_name}`}
                >
                  {userDetails?.first_name?.[0]?.toUpperCase() || (
                    <LuUser className="size-5 text-white" />
                  )}
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-48 ml-12"
                side="top"
                align="start"
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
      )}
    </div>
  );
};

export default SidebarDesktop;
