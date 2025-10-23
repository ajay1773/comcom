import React from "react";
import { Card } from "../ui/card";

interface StatusCardProps {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  actions?: React.ReactNode;
}

const StatusCard: React.FC<StatusCardProps> = ({
  icon,
  title,
  subtitle,
  actions,
}) => {
  return (
    <Card className="max-w-sm mx-auto p-4 sm:p-6 text-center rounded-lg sm:rounded-xl border border-border">
      {/* Icon container with circular background */}
      <div className="flex justify-center mb-3 sm:mb-4">
        <div className="rounded-full flex items-center justify-center">
          {icon}
        </div>
      </div>

      <div className="flex flex-col items-center justify-center space-y-1.5 sm:space-y-2">
        {/* Title */}
        <h2 className="text-lg sm:text-xl font-semibold text-foreground leading-tight">
          {title}
        </h2>

        {/* Subtitle */}
        <p className="text-muted-foreground text-xs sm:text-sm leading-relaxed max-w-xs">
          {subtitle}
        </p>
      </div>

      {/* Actions (if provided) */}
      {actions && <div className="mt-4 sm:mt-5">{actions}</div>}
    </Card>
  );
};

export default StatusCard;
