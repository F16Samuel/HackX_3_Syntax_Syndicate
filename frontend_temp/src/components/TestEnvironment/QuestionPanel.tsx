import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Question } from "@/data/questions";

interface QuestionPanelProps {
  question: Question;
  currentIndex: number;
  totalQuestions: number;
  onNext: () => void;
  onPrev: () => void;
}

export const QuestionPanel = ({
  question,
  currentIndex,
  totalQuestions,
  onNext,
  onPrev,
}: QuestionPanelProps) => {
  const difficultyColors = {
    Easy: "bg-green-500",
    Medium: "bg-yellow-500",
    Hard: "bg-red-500",
  };

  return (
    <Card className="h-full bg-card border-border">
      <div className="p-6 border-b border-border">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-foreground">
              Problem {currentIndex + 1}: {question.title}
            </h2>
            <Badge
              className={`${difficultyColors[question.difficulty]} text-white`}
            >
              {question.difficulty}
            </Badge>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={onPrev}
              disabled={currentIndex === 0}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm text-muted-foreground">
              {currentIndex + 1} / {totalQuestions}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={onNext}
              disabled={currentIndex === totalQuestions - 1}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div className="flex gap-2 text-sm text-muted-foreground">
          <span>Points: 100</span>
        </div>
      </div>

      <ScrollArea className="h-[calc(100%-120px)]">
        <div className="p-6 space-y-4 text-foreground">
          <div>
            <h3 className="font-semibold mb-2">Description</h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {question.description.split("\n").map((line, idx) => (
                <span key={idx}>
                  {line}
                  <br />
                </span>
              ))}
            </p>
          </div>

          {question.examples.map((example, idx) => (
            <div key={idx}>
              <h3 className="font-semibold mb-2">Example {idx + 1}</h3>
              <div className="bg-secondary p-4 rounded-lg text-sm font-mono space-y-1">
                <div>
                  <span className="text-primary">Input:</span>{" "}
                  <span className="text-muted-foreground">{example.input}</span>
                </div>
                <div>
                  <span className="text-primary">Output:</span>{" "}
                  <span className="text-muted-foreground">{example.output}</span>
                </div>
                <div>
                  <span className="text-primary">Explanation:</span>{" "}
                  <span className="text-muted-foreground">
                    {example.explanation}
                  </span>
                </div>
              </div>
            </div>
          ))}

          <div>
            <h3 className="font-semibold mb-2">Constraints</h3>
            <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
              {question.constraints.map((constraint, idx) => (
                <li key={idx}>{constraint}</li>
              ))}
            </ul>
          </div>
        </div>
      </ScrollArea>
    </Card>
  );
};
