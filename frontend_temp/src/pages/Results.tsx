import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle2, XCircle, Clock } from "lucide-react";

interface ScoreResult {
  questionId: string;
  questionTitle: string;
  score: {
    prompt_quality?: { score: number; justification: string };
    answer_accuracy?: { score: number; justification: string };
    creativity_innovation?: { score: number; justification: string };
    overall?: { score: number; justification: string };
  };
}

const Results = () => {
  const [results, setResults] = useState<ScoreResult[]>([]);
  const [totalTime, setTotalTime] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    const storedResults = sessionStorage.getItem("testResults");
    const storedTime = sessionStorage.getItem("totalTime");

    if (!storedResults) {
      navigate("/");
      return;
    }

    setResults(JSON.parse(storedResults));
    setTotalTime(parseFloat(storedTime || "0"));
  }, [navigate]);

  const totalScore = results.reduce(
    (sum, r) => sum + (r.score.overall?.score || 0),
    0
  );
  const maxScore = results.length * 30;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <Card className="p-6 bg-card border-border">
          <h1 className="text-3xl font-bold text-foreground mb-4">
            Test Results
          </h1>
          <div className="flex items-center gap-6 mb-6">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-primary" />
              <span className="text-muted-foreground">
                Time Taken: {formatTime(totalTime)}
              </span>
            </div>
          </div>
          <div className="text-center py-6 border-t border-border">
            <div className="text-4xl font-bold text-primary mb-2">
              {totalScore} / {maxScore}
            </div>
            <div className="text-muted-foreground">
              {Math.round((totalScore / maxScore) * 100)}% Score
            </div>
          </div>
        </Card>

        {results.map((result, idx) => (
          <Card key={result.questionId} className="p-6 bg-card border-border">
            <h2 className="text-xl font-semibold text-foreground mb-4">
              Question {idx + 1}: {result.questionTitle}
            </h2>

            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-secondary rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">
                    Prompt Quality
                  </div>
                  <div className="text-2xl font-bold text-foreground">
                    {result.score.prompt_quality?.score ?? 0}/10
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {result.score.prompt_quality?.justification}
                  </div>
                </div>

                <div className="p-4 bg-secondary rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">
                    Answer Accuracy
                  </div>
                  <div className="text-2xl font-bold text-foreground">
                    {result.score.answer_accuracy?.score ?? 0}/10
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {result.score.answer_accuracy?.justification}
                  </div>
                </div>

                <div className="p-4 bg-secondary rounded-lg">
                  <div className="text-sm text-muted-foreground mb-1">
                    Creativity & Innovation
                  </div>
                  <div className="text-2xl font-bold text-foreground">
                    {result.score.creativity_innovation?.score ?? 0}/10
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {result.score.creativity_innovation?.justification}
                  </div>
                </div>
              </div>

              <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
                <div className="text-sm text-muted-foreground mb-1">
                  Overall Score
                </div>
                <div className="text-3xl font-bold text-primary">
                  {result.score.overall?.score ?? 0}/30
                </div>
                <div className="text-sm text-muted-foreground mt-2">
                  {result.score.overall?.justification}
                </div>
              </div>
            </div>
          </Card>
        ))}

        <div className="flex justify-center gap-4">
          <Button
            onClick={() => navigate("https://advent-hackx.vercel.app")}
            className="bg-gradient-primary hover:bg-gradient-primary-hover text-foreground shadow-glow"
          >
            Return Home
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Results;
