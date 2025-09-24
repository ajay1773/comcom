import { useTheme } from "next-themes";
import { Toaster as Sonner } from "sonner";
import type { ToasterProps as SonnerToasterProps } from "sonner";

const Toaster = ({ ...props }: SonnerToasterProps) => {
  const { theme = "system" } = useTheme();

  return (
    <Sonner
      theme={theme as SonnerToasterProps["theme"]}
      className="toaster group"
      style={
        {
          "--normal-bg": "var(--popover)",
          "--normal-text": "var(--popover-foreground)",
          "--normal-border": "var(--border)",
        } as React.CSSProperties
      }
      {...props}
    />
  );
};

export { Toaster };
