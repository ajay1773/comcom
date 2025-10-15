import { Button } from "@/components/ui/button";
import { LuBrainCircuit } from "react-icons/lu";

interface ChatHeaderProps {
  isLoggedIn: boolean;
  onSignIn?: () => void;
  onSignUp?: () => void;
}

const ChatHeader = ({ isLoggedIn, onSignIn, onSignUp }: ChatHeaderProps) => {
  if (isLoggedIn) return null; // Don't show header for logged-in users

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-sm">
      <div className="px-6 h-16 flex items-center justify-between w-full">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <LuBrainCircuit className="text-blue-500 size-[40px]" />

          <span className="text-xl font-semibold text-foreground">ComCom</span>
        </div>

        {/* Auth Buttons */}
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={onSignIn}
            className="text-sm font-medium"
          >
            Log in
          </Button>
          <Button size="sm" onClick={onSignUp} className="text-sm font-medium">
            Sign up for free
          </Button>
        </div>
      </div>
    </header>
  );
};

export default ChatHeader;
