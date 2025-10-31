import { useState, useEffect } from "react";
import Editor from "@monaco-editor/react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Play, Send, Terminal } from "lucide-react";
import { toast } from "@/hooks/use-toast";
import { ScrollArea } from "@/components/ui/scroll-area";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface OutputResult {
  stdout?: string;
  stderr?: string;
  error?: string;
  input?: any;
  expected?: string;
  actual?: string;
  passed?: boolean;
}

const defaultCode = {
  python: `def twoSum(nums, target):
    # Write your solution here
    pass`,
  cpp: `#include <vector>
using namespace std;

vector<int> twoSum(vector<int>& nums, int target) {
    // Write your solution here
    return {};
}`,
  java: `public class Solution {
    public int[] twoSum(int[] nums, int target) {
        // Write your solution here
        return new int[]{};
    }
}`,
};

const getMonacoLanguage = (lang: string) => {
  const map: { [key: string]: string } = {
    python: "python",
    cpp: "cpp",
    java: "java",
  };
  return map[lang] || "python";
};

interface CodeEditorProps {
  questionId: string;
  language: string;
  code: string;
  onCodeChange: (code: string) => void;
  testCases: Array<{ input: any; expected: string }>;
}

export const CodeEditor = ({
  questionId,
  language: initialLanguage,
  code: initialCode,
  onCodeChange,
  testCases,
}: CodeEditorProps) => {
  const [code, setCode] = useState(initialCode);
  const [output, setOutput] = useState<OutputResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState<"python" | "cpp" | "java">(
    initialLanguage === "python" ? "python" : "python"
  );

  // Sync with prop changes
  useEffect(() => {
    setCode(initialCode);
  }, [initialCode, questionId]);

  const handleCodeChange = (value: string | undefined) => {
    const newCode = value || "";
    setCode(newCode);
    onCodeChange(newCode);
  };

  const handleRun = async () => {
    if (!code.trim()) {
      toast({
        title: "Error",
        description: "Please write some code first.",
      });
      return;
    }

    setLoading(true);
    setOutput([]);

    toast({
      title: "Running Code",
      description: "Executing your solution...",
    });

    try {
      const response = await fetch(`${API_BASE_URL}/api/compile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          language: language,
          code: code,
          test_cases: testCases,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Compilation failed");
      }

      const data = await response.json();
      setOutput(data.results || []);

      // Check if there are any errors
      const hasErrors = data.results?.some(
        (r: OutputResult) => r.stderr || r.error || (r.passed === false && !r.actual)
      ) ?? false;
      
      const allPassed = data.results?.every((r: OutputResult) => r.passed === true) ?? false;
      
      toast({
        title: hasErrors ? "Error" : allPassed ? "Success" : "Some tests failed",
        description: hasErrors
          ? "Compilation or runtime error occurred"
          : allPassed
          ? "All test cases passed!"
          : "Check the output for details.",
        variant: hasErrors ? "destructive" : undefined,
      });
    } catch (error) {
      console.error("Error:", error);
      setOutput([
        {
          error: error instanceof Error ? error.message : "Failed to compile or run code. Please check your code syntax.",
        },
      ]);
      toast({
        title: "Error",
        description: "Failed to execute code. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = () => {
    toast({
      title: "Submitting Solution",
      description: "Your solution has been submitted for evaluation.",
    });
    // Placeholder for submission logic
  };

  const formatOutput = (result: OutputResult, index: number) => {
    // Show compilation errors first
    if (result.stderr) {
      return (
        <div key={index} className="p-3 rounded-lg border mb-2 bg-red-900/20 border-red-700">
          <div className="text-xs font-semibold mb-2 text-red-400">Compilation Error:</div>
          <div className="text-xs font-mono text-red-300 whitespace-pre-wrap break-words">
            {result.stderr}
          </div>
        </div>
      );
    }

    if (result.error) {
      return (
        <div key={index} className="p-3 rounded-lg border mb-2 bg-red-900/20 border-red-700">
          <div className="text-xs font-semibold mb-2 text-red-400">Error:</div>
          <div className="text-xs font-mono text-red-300">{result.error}</div>
        </div>
      );
    }

    if (result.input !== undefined) {
      // Test case result
      const hasError = !result.passed && !result.actual && result.stderr;
      return (
        <div
          key={index}
          className={`p-3 rounded-lg border mb-2 ${
            result.passed
              ? "bg-green-900/20 border-green-700 text-green-300"
              : hasError
              ? "bg-red-900/20 border-red-700 text-red-300"
              : "bg-red-900/20 border-red-700 text-red-300"
          }`}
        >
          <div className="text-xs font-semibold mb-1">
            Test Case {index + 1} {result.passed ? "✓ Passed" : "✗ Failed"}
          </div>
          {hasError && result.stderr && (
            <div className="text-xs font-mono text-red-300 mb-2 whitespace-pre-wrap">
              Error: {result.stderr}
            </div>
          )}
          <div className="text-xs space-y-1 font-mono">
            <div>
              <span className="opacity-70">Input:</span> {JSON.stringify(result.input)}
            </div>
            <div>
              <span className="opacity-70">Expected:</span> {result.expected}
            </div>
            <div>
              <span className="opacity-70">Got:</span> {result.actual || "(empty)"}
            </div>
          </div>
        </div>
      );
    }

    // Direct output
    return (
      <div key={index} className="text-sm font-mono space-y-1">
        {result.stdout && (
          <div className="text-green-300">
            <span className="text-green-500">Output:</span> {result.stdout}
          </div>
        )}
        {result.stderr && (
          <div className="text-red-300 whitespace-pre-wrap">
            <span className="text-red-500">Error:</span> {result.stderr}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col gap-2">
      {/* Code Editor */}
      <Card className="flex-1 bg-card border-border flex flex-col overflow-hidden min-h-0">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-foreground">Code Editor</h3>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as "python" | "cpp" | "java")}
              className="ml-2 px-2 py-1 bg-secondary border border-border rounded text-sm text-foreground"
            >
              <option value="python">Python</option>
              <option value="cpp">C++</option>
              <option value="java">Java</option>
            </select>
          </div>
          <div className="flex gap-2">
            <Button
              onClick={handleRun}
              variant="outline"
              size="sm"
              disabled={loading}
              className="border-primary text-primary hover:bg-primary hover:text-foreground transition-smooth"
            >
              <Play className="h-4 w-4 mr-1" />
              {loading ? "Running..." : "Run"}
            </Button>
            <Button
              onClick={handleSubmit}
              size="sm"
              className="bg-gradient-primary hover:bg-gradient-primary-hover text-foreground shadow-glow"
            >
              <Send className="h-4 w-4 mr-1" />
              Submit
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-hidden">
          <Editor
            height="100%"
            language={getMonacoLanguage(language)}
            value={code}
            onChange={handleCodeChange}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: "on",
              roundedSelection: false,
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 2,
              padding: { top: 16, bottom: 16 },
            }}
          />
        </div>
      </Card>

      {/* Output Box */}
      <Card className="h-64 bg-card border-border flex flex-col overflow-hidden">
        <div className="p-3 border-b border-border flex items-center gap-2">
          <Terminal className="h-4 w-4 text-primary" />
          <h3 className="font-semibold text-sm text-foreground">Output</h3>
        </div>
        <ScrollArea className="flex-1 p-3">
          {output.length === 0 ? (
            <div className="text-muted-foreground text-sm text-center py-4">
              No output yet. Run your code to see results.
            </div>
          ) : (
            <div className="space-y-2">
              {output.map((result, index) => formatOutput(result, index))}
            </div>
          )}
        </ScrollArea>
      </Card>
    </div>
  );
};
