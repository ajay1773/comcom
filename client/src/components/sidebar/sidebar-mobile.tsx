import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import SidebarBase from "./sidebar-base";

interface SidebarMobileProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const SidebarMobile = ({ open, onOpenChange }: SidebarMobileProps) => {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="w-64 p-0">
        <SheetHeader className="sr-only">
          <SheetTitle>Navigation</SheetTitle>
        </SheetHeader>
        <SidebarBase onConversationClick={() => onOpenChange(false)} />
      </SheetContent>
    </Sheet>
  );
};

export default SidebarMobile;
