import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, Shield, Eye, Clock } from "lucide-react";

interface StartScreenProps {
  onStart: () => void;
}

export const StartScreen = ({ onStart }: StartScreenProps) => {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <Card className="max-w-2xl w-full bg-card border-border p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-primary rounded-full mb-4 shadow-glow">
            <Shield className="h-8 w-8 text-foreground" />
          </div>
          <h1 className="text-3xl font-bold text-foreground mb-2">Technical Assessment</h1>
          <p className="text-muted-foreground">
            Read the proctoring rules carefully before starting
          </p>
        </div>

        <div className="space-y-6 mb-8">
          <div className="bg-secondary p-4 rounded-lg border border-border">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-foreground mb-1">Proctoring Rules</h3>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-primary" />
                    Fullscreen mode is mandatory throughout the test
                  </li>
                  <li className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-primary" />
                    Switching tabs will auto-submit your test
                  </li>
                  <li className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-primary" />
                    Minimizing the window will auto-submit your test
                  </li>
                  <li className="flex items-center gap-2">
                    <Eye className="h-4 w-4 text-primary" />
                    Copy and paste operations are disabled
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-secondary p-4 rounded-lg border border-border">
            <div className="flex items-start gap-3">
              <Clock className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-foreground mb-1">Test Details</h3>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>Duration: 45 minutes</li>
                  <li>Questions: 2 coding problems</li>
                  <li>Language: JavaScript (more languages available)</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <Button
          onClick={onStart}
          className="w-full bg-gradient-primary hover:bg-gradient-primary-hover text-foreground shadow-glow h-12 text-lg font-semibold"
        >
          Start Test
        </Button>

        <p className="text-center text-xs text-muted-foreground mt-4">
          By starting this test, you agree to the proctoring rules above
        </p>
      </Card>
    </div>
  );
};
