import { useEffect, useState } from "react";
import { toast } from "@/hooks/use-toast";

export const useFullscreenEnforcement = (onSubmit: () => void) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);
  const [isBlocked, setIsBlocked] = useState(false);

  useEffect(() => {
    const handleFullscreenChange = () => {
      const isCurrentlyFullscreen = !!document.fullscreenElement;
      setIsFullscreen(isCurrentlyFullscreen);

      if (hasStarted && !isCurrentlyFullscreen) {
        setIsBlocked(true);
      } else if (hasStarted && isCurrentlyFullscreen) {
        setIsBlocked(false);
      }
    };

    const handleVisibilityChange = () => {
      if (hasStarted && document.hidden) {
        toast({
          title: "Test Submitted",
          description: "Test automatically submitted due to tab switch.",
          variant: "destructive",
        });
        onSubmit();
      }
    };

    const handleBlur = () => {
      if (hasStarted) {
        toast({
          title: "Test Submitted",
          description: "Test automatically submitted due to window minimization.",
          variant: "destructive",
        });
        onSubmit();
      }
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("blur", handleBlur);

    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("blur", handleBlur);
    };
  }, [hasStarted, onSubmit]);

  const enterFullscreen = async () => {
    try {
      await document.documentElement.requestFullscreen();
      setHasStarted(true);
      setIsFullscreen(true);
      setIsBlocked(false);
    } catch (error) {
      toast({
        title: "Fullscreen Error",
        description: "Unable to enter fullscreen mode. Please try again.",
        variant: "destructive",
      });
    }
  };

  const resumeFullscreen = async () => {
    try {
      await document.documentElement.requestFullscreen();
      setIsBlocked(false);
    } catch (error) {
      toast({
        title: "Fullscreen Error",
        description: "Unable to enter fullscreen mode. Please try again.",
        variant: "destructive",
      });
    }
  };

  return { isFullscreen, hasStarted, isBlocked, enterFullscreen, resumeFullscreen };
};
