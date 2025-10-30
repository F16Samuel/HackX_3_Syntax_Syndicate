// Placeholder data for development - replace with API calls later

export const placeholderCandidates = [
  { id: 1, name: 'John Doe', email: 'john.doe@example.com' },
  { id: 2, name: 'Jane Smith', email: 'jane.smith@example.com' },
  { id: 3, name: 'Bob Johnson', email: 'bob.johnson@example.com' },
  { id: 4, name: 'Alice Williams', email: 'alice.williams@example.com' },
  { id: 5, name: 'Charlie Brown', email: 'charlie.brown@example.com' },
]

export const placeholderTests = [
  {
    id: 1,
    title: 'Senior Backend Engineer Assessment',
    promptBudget: 10000,
    rubrics: {
      promptEfficiency: 0.3,
      answerAccuracy: 0.5,
      creativityAndInnovation: 0.2,
    },
    questions: [
      {
        id: 1,
        type: 'Data Structures & Algorithms',
        question: 'Implement a binary search tree with insert and search operations.',
        additionalConstraints: 'Time complexity must be O(log n) for both operations.',
      },
    ],
    candidateIds: [1, 2, 3],
    createdAt: '2024-01-15T10:00:00Z',
  },
  {
    id: 2,
    title: 'Cloud Architecture Challenge',
    promptBudget: 15000,
    rubrics: {
      promptEfficiency: 0.25,
      answerAccuracy: 0.4,
      creativityAndInnovation: 0.35,
    },
    questions: [
      {
        id: 1,
        type: 'Cloud Computing',
        question: 'Design a scalable microservices architecture for an e-commerce platform.',
        additionalConstraints: 'Must support 1M+ concurrent users.',
      },
    ],
    candidateIds: [2, 4, 5],
    createdAt: '2024-01-16T14:30:00Z',
  },
]

export const placeholderResults = {
  1: [
    { candidateId: 1, score: 85.5, submittedAt: '2024-01-20T10:30:00Z' },
    { candidateId: 2, score: 92.3, submittedAt: '2024-01-20T11:15:00Z' },
    { candidateId: 3, score: 78.1, submittedAt: '2024-01-20T12:00:00Z' },
  ],
  2: [
    { candidateId: 2, score: 88.7, submittedAt: '2024-01-21T09:00:00Z' },
    { candidateId: 4, score: 91.2, submittedAt: '2024-01-21T10:20:00Z' },
    { candidateId: 5, score: 76.4, submittedAt: '2024-01-21T11:45:00Z' },
  ],
}

// API helper functions - replace with actual API calls
export const api = {
  getTests: async () => {
    // TODO: Replace with actual API call
    return new Promise((resolve) => setTimeout(() => resolve(placeholderTests), 500))
  },
  
  getCandidates: async () => {
    // TODO: Replace with actual API call
    return new Promise((resolve) => setTimeout(() => resolve(placeholderCandidates), 500))
  },
  
  createTest: async (testData) => {
    // TODO: Replace with actual API call
    const newTest = {
      id: Date.now(),
      ...testData,
      createdAt: new Date().toISOString(),
    }
    placeholderTests.push(newTest)
    return new Promise((resolve) => setTimeout(() => resolve(newTest), 500))
  },
  
  updateTest: async (testId, testData) => {
    // TODO: Replace with actual API call
    const index = placeholderTests.findIndex(t => t.id === testId)
    if (index !== -1) {
      placeholderTests[index] = { ...placeholderTests[index], ...testData }
      return new Promise((resolve) => setTimeout(() => resolve(placeholderTests[index]), 500))
    }
    throw new Error('Test not found')
  },
  
  getTestResults: async (testId) => {
    // TODO: Replace with actual API call
    return new Promise((resolve) => setTimeout(() => resolve(placeholderResults[testId] || []), 500))
  },
}


