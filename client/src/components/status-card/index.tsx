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
    <Card className="max-w-md mx-auto p-8 text-center rounded-2xl shadow-sm ">
      {/* Icon container with circular background */}
      <div className="flex justify-center">
        <div className="rounded-full flex items-center justify-center">
          {icon}
        </div>
      </div>

      <div className="flex flex-col items-center justify-center mt-4">
        {/* Title */}
        <h2 className="text-xl font-semibold text-foreground mb-2 leading-tight">
          {title}
        </h2>

        {/* Subtitle */}
        <p className="text-gray-500 text-base leading-relaxed">{subtitle}</p>
      </div>
      {/* Actions (if provided) */}
      {actions && <div className="mt-6">{actions}</div>}
    </Card>
  );
};

export default StatusCard;
