import { useState } from "react";
import { Button } from "@/components/ui/button";
import { LuBrainCircuit } from "react-icons/lu";
import SigninDrawer from "@/features/signin/views/signin-drawer";
import SignupDrawer from "@/features/signup/views/signup-drawer";

interface ChatHeaderProps {
  isLoggedIn: boolean;
}

const ChatHeader = ({ isLoggedIn }: ChatHeaderProps) => {
  const [signinModalOpen, setSigninModalOpen] = useState(false);
  const [signupModalOpen, setSignupModalOpen] = useState(false);

  if (isLoggedIn) return null; // Don't show header for logged-in users

  return (
    <>
      <header className="w-full bg-background/80 backdrop-blur-sm border-b border-neutral-700/30">
        <div className="px-3 sm:px-4 md:px-6 h-14 sm:h-16 flex items-center justify-between w-full">
          {/* Logo */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            <LuBrainCircuit className="text-blue-500 size-[28px] sm:size-[32px] md:size-[40px]" />

            <span className="text-base sm:text-lg md:text-xl font-semibold text-foreground">
              ComCom
            </span>
          </div>

          {/* Auth Buttons */}
          <div className="flex items-center gap-1.5 sm:gap-2 md:gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSigninModalOpen(true)}
              className="text-xs sm:text-sm font-medium h-8 sm:h-9 px-2 sm:px-3"
            >
              Log in
            </Button>
            <Button
              size="sm"
              onClick={() => setSignupModalOpen(true)}
              className="text-xs sm:text-sm font-medium h-8 sm:h-9 px-2 sm:px-4"
            >
              Sign up for free
            </Button>
          </div>
        </div>
      </header>

      <SigninDrawer open={signinModalOpen} onOpenChange={setSigninModalOpen} />
      <SignupDrawer open={signupModalOpen} onOpenChange={setSignupModalOpen} />
    </>
  );
};

export default ChatHeader;
