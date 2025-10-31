import { AlertTriangle, Maximize } from "lucide-react";
import { Button } from "@/components/ui/button";

interface FullscreenBlockerProps {
  onResume: () => void;
}

export const FullscreenBlocker = ({ onResume }: FullscreenBlockerProps) => {
  return (
    <div className="fixed inset-0 bg-background z-50 flex items-center justify-center">
      <div className="text-center max-w-md px-6">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-destructive/10 rounded-full mb-6 animate-pulse">
          <AlertTriangle className="h-10 w-10 text-destructive" />
        </div>
        
        <h2 className="text-2xl font-bold text-foreground mb-3">
          Fullscreen Required
        </h2>
        
        <p className="text-muted-foreground mb-8 leading-relaxed">
          You have exited fullscreen mode. To continue your test, please click the button below to return to fullscreen.
        </p>
        
        <Button
          onClick={onResume}
          size="lg"
          className="bg-gradient-primary hover:bg-gradient-primary-hover text-foreground shadow-glow h-14 px-8 text-lg font-semibold"
        >
          <Maximize className="h-5 w-5 mr-2" />
          Return to Fullscreen
        </Button>

        <p className="text-xs text-muted-foreground mt-6">
          Warning: Switching tabs or minimizing will auto-submit your test
        </p>
      </div>
    </div>
  );
};
