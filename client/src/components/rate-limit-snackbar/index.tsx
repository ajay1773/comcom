import { useEffect, useState } from "react";
import { useChatStore } from "@/store/chat-store";
import { X, Clock, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";

export function RateLimitSnackbar() {
  const rateLimitStatus = useChatStore((state) => state.rateLimitStatus);
  const clearRateLimitError = useChatStore(
    (state) => state.clearRateLimitError
  );
  const [isVisible, setIsVisible] = useState(false);
  const [countdown, setCountdown] = useState<number | null>(null);

  useEffect(() => {
    if (rateLimitStatus.isRateLimited) {
      setIsVisible(true);

      // Set up countdown if retryAfter is available
      if (rateLimitStatus.retryAfter) {
        setCountdown(rateLimitStatus.retryAfter);

        const interval = setInterval(() => {
          setCountdown((prev) => {
            if (prev === null || prev <= 1) {
              clearInterval(interval);
              // Auto-clear rate limit after countdown
              setTimeout(() => {
                clearRateLimitError();
                setIsVisible(false);
              }, 1000);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);

        return () => clearInterval(interval);
      }
    } else {
      setIsVisible(false);
      setCountdown(null);
    }
  }, [
    rateLimitStatus.isRateLimited,
    rateLimitStatus.retryAfter,
    clearRateLimitError,
  ]);

  const handleClose = () => {
    setIsVisible(false);
    clearRateLimitError();
  };

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  if (!isVisible || !rateLimitStatus.isRateLimited) {
    return null;
  }

  return (
    <div className="animate-in slide-in-from-bottom-5 w-full mb-3">
      <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg w-full">
        <div className="px-4 py-2.5 flex items-center gap-3">
          {/* Icon */}
          <div className="flex-shrink-0">
            <AlertCircle className="h-4 w-4 text-orange-400" />
          </div>

          {/* Content - Single Line */}
          <div className="flex-1 min-w-0 flex items-center gap-2">
            <span className="text-sm text-orange-200 font-medium truncate">
              {rateLimitStatus.message}
            </span>

            {/* Countdown */}
            {rateLimitStatus.limitType === "requests" &&
              countdown !== null &&
              countdown > 0 && (
                <span className="text-xs text-orange-300/80 flex items-center gap-1 flex-shrink-0">
                  <Clock className="h-3 w-3" />
                  {formatTime(countdown)}
                </span>
              )}

            {/* Token usage for logged-in users */}
            {rateLimitStatus.limitType === "tokens" &&
              rateLimitStatus.tokensUsed &&
              rateLimitStatus.dailyLimit && (
                <span className="text-xs text-orange-300/80 flex-shrink-0">
                  {rateLimitStatus.tokensUsed?.toLocaleString()} /{" "}
                  {rateLimitStatus.dailyLimit?.toLocaleString()} tokens
                </span>
              )}
          </div>

          {/* Close button */}
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6 hover:bg-orange-500/20 flex-shrink-0"
            onClick={handleClose}
          >
            <X className="h-3.5 w-3.5 text-orange-300" />
          </Button>
        </div>
      </div>
    </div>
  );
}
