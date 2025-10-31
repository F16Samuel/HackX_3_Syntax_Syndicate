import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { StartScreen } from "@/components/TestEnvironment/StartScreen";
import { SidebarChat } from "@/components/TestEnvironment/SidebarChat";
import { QuestionPanel } from "@/components/TestEnvironment/QuestionPanel";
import { CodeEditor } from "@/components/TestEnvironment/CodeEditor";
import { QueryChat } from "@/components/TestEnvironment/QueryChat";
import { FullscreenBlocker } from "@/components/TestEnvironment/FullscreenBlocker";
import { useFullscreenEnforcement } from "@/hooks/useFullscreenEnforcement";
import { useCopyPastePrevention } from "@/hooks/useCopyPastePrevention";
import { toast } from "@/hooks/use-toast";
import { questions, Question } from "@/data/questions";

const Index = () => {
  const [testStarted, setTestStarted] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questionCode, setQuestionCode] = useState<Record<string, string>>({});
  const [promptCounts, setPromptCounts] = useState<Record<string, number>>({});
  const [startTime] = useState(Date.now());
  const navigate = useNavigate();

  // Initialize code for each question
  useEffect(() => {
    const initialCode: Record<string, string> = {};
    questions.forEach((q) => {
      initialCode[q.id] = getDefaultCode(q);
    });
    setQuestionCode(initialCode);
    setPromptCounts(
      questions.reduce((acc, q) => ({ ...acc, [q.id]: 0 }), {})
    );
  }, []);

  const getDefaultCode = (question: Question) => {
    if (question.id === "question_1") {
      return `def twoSum(nums, target):
    # Write your solution here
    pass`;
    } else if (question.id === "question_2") {
      return `def reverseString(s):
    # Write your solution here
    pass`;
    }
    return "";
  };

  const currentQuestion = questions[currentQuestionIndex];

  const handleSubmit = async () => {
    toast({
      title: "Submitting Test",
      description: "Evaluating your solutions...",
    });

    try {
      // Calculate scores for each question
      const scores = await Promise.all(
        questions.map(async (q) => {
          const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
          const promptCount = promptCounts[q.id] || 0;

          // Get candidate answer from code output
          const candidateAnswer = questionCode[q.id] || "";

          const response = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/score`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              question_id: q.id,
              payload: {
                candidate_answer: candidateAnswer,
                expected_answer: q.expectedAnswer,
                elapsed_seconds: elapsedSeconds,
                prompt_count: promptCount,
                notes: `Question: ${q.title}`,
              },
            }),
          });

          if (!response.ok) {
            throw new Error(`Failed to score question ${q.id}`);
          }

          const data = await response.json();
          return {
            questionId: q.id,
            questionTitle: q.title,
            score: data.reply,
          };
        })
      );

      // Store results and navigate
      sessionStorage.setItem("testResults", JSON.stringify(scores));
      sessionStorage.setItem("totalTime", ((Date.now() - startTime) / 1000).toString());

      // Exit fullscreen
      if (document.fullscreenElement) {
        document.exitFullscreen();
      }

      setTestStarted(false);
      navigate("/results");
    } catch (error) {
      console.error("Error submitting:", error);
      toast({
        title: "Submission Error",
        description: "Failed to submit test. Please try again.",
        variant: "destructive",
      });
    }
  };

  const { hasStarted, isBlocked, enterFullscreen, resumeFullscreen } =
    useFullscreenEnforcement(handleSubmit);
  useCopyPastePrevention(hasStarted);

  const handleStart = async () => {
    await enterFullscreen();
    setTestStarted(true);
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrevQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const incrementPromptCount = (questionId: string) => {
    setPromptCounts((prev) => ({
      ...prev,
      [questionId]: (prev[questionId] || 0) + 1,
    }));
  };

  if (!testStarted) {
    return <StartScreen onStart={handleStart} />;
  }

  return (
    <>
      {isBlocked && <FullscreenBlocker onResume={resumeFullscreen} />}

      <div className="h-screen w-full flex bg-background overflow-hidden select-none">
        <div className="w-80 border-r border-border">
          <QueryChat
            questionId={currentQuestion.id}
            questionInfo={currentQuestion.title}
            onPrompt={() => incrementPromptCount(currentQuestion.id)}
          />
        </div>

        <div className="flex-1 flex flex-col p-4 gap-4 overflow-hidden">
          <div className="flex-1">
            <QuestionPanel
              question={currentQuestion}
              currentIndex={currentQuestionIndex}
              totalQuestions={questions.length}
              onNext={handleNextQuestion}
              onPrev={handlePrevQuestion}
            />
          </div>

          <div className="flex-1">
            <CodeEditor
              questionId={currentQuestion.id}
              language={questionCode[currentQuestion.id]?.split("\n")[0].includes("def") ? "python" : "python"}
              code={questionCode[currentQuestion.id] || getDefaultCode(currentQuestion)}
              onCodeChange={(code) =>
                setQuestionCode((prev) => ({
                  ...prev,
                  [currentQuestion.id]: code,
                }))
              }
              testCases={currentQuestion.testCases}
            />
          </div>
        </div>

        <SidebarChat
          questionId={currentQuestion.id}
          questionInfo={currentQuestion.title}
          onPrompt={() => incrementPromptCount(currentQuestion.id)}
        />
      </div>
    </>
  );
};

export default Index;
