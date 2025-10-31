export interface Question {
  id: string;
  title: string;
  difficulty: "Easy" | "Medium" | "Hard";
  description: string;
  examples: Array<{
    input: string;
    output: string;
    explanation: string;
  }>;
  constraints: string[];
  testCases: Array<{
    input: any;
    expected: string;
  }>;
  expectedAnswer: string;
}

export const questions: Question[] = [
  {
    id: "question_1",
    title: "Two Sum",
    difficulty: "Medium",
    description: `Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.`,
    examples: [
      {
        input: "nums = [2,7,11,15], target = 9",
        output: "[0,1]",
        explanation: "Because nums[0] + nums[1] == 9, we return [0, 1].",
      },
      {
        input: "nums = [3,2,4], target = 6",
        output: "[1,2]",
        explanation: "Because nums[1] + nums[2] == 6, we return [1, 2].",
      },
    ],
    constraints: [
      "2 ≤ nums.length ≤ 10⁴",
      "-10⁹ ≤ nums[i] ≤ 10⁹",
      "-10⁹ ≤ target ≤ 10⁹",
      "Only one valid answer exists",
    ],
    testCases: [
      { input: [[2, 7, 11, 15], 9], expected: "[0,1]" },
      { input: [[3, 2, 4], 6], expected: "[1,2]" },
      { input: [[3, 3], 6], expected: "[0,1]" },
    ],
    expectedAnswer: "[0,1]",
  },
  {
    id: "question_2",
    title: "Reverse String",
    difficulty: "Easy",
    description: `Write a function that reverses a string. The input string is given as an array of characters s. You must do this by modifying the input array in-place with O(1) extra memory.`,
    examples: [
      {
        input: "s = [\"h\",\"e\",\"l\",\"l\",\"o\"]",
        output: "[\"o\",\"l\",\"l\",\"e\",\"h\"]",
        explanation: "The string is reversed in place.",
      },
      {
        input: "s = [\"H\",\"a\",\"n\",\"n\",\"a\",\"h\"]",
        output: "[\"h\",\"a\",\"n\",\"n\",\"a\",\"H\"]",
        explanation: "The string is reversed in place.",
      },
    ],
    constraints: [
      "1 ≤ s.length ≤ 10⁵",
      "s[i] is a printable ascii character",
    ],
    testCases: [
      { input: [["h", "e", "l", "l", "o"]], expected: "o,l,l,e,h" },
      { input: [["H", "a", "n", "n", "a", "h"]], expected: "h,a,n,n,a,H" },
    ],
    expectedAnswer: "o,l,l,e,h",
  },
];
