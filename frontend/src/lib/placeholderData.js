// Placeholder data for development - replace with API calls later

export const placeholderCandidates = [
  { id: 1, name: 'Priya Sharma', email: 'priya.sharma@example.com' },
  { id: 2, name: 'Rohan Gupta', email: 'rohan.gupta@example.com' },
  { id: 3, name: 'Amit Singh', email: 'amit.singh@example.com' },
  { id: 4, name: 'Meera Patel', email: 'meera.patel@example.com' },
  { id: 5, name: 'Vikram Rao', email: 'vikram.rao@example.com' },
  { id: 6, name: 'Anjali Desai', email: 'anjali.desai@example.com' },
  { id: 7, name: 'Sandeep Kumar', email: 'sandeep.kumar@example.com' },
  { id: 8, name: 'Deepika Reddy', email: 'deepika.reddy@example.com' },
  { id: 9, name: 'Arjun Nair', email: 'arjun.nair@example.com' },
  { id: 10, name: 'Neha Joshi', email: 'neha.joshi@example.com' },
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
    candidateIds: [1, 2, 3, 6, 9], // Priya, Rohan, Amit, Anjali, Arjun
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
    candidateIds: [2, 4, 5, 7, 10], // Rohan, Meera, Vikram, Sandeep, Neha
    createdAt: '2024-01-16T14:30:00Z',
  },
  {
    id: 3,
    title: 'Frontend Developer Task',
    promptBudget: 8000,
    rubrics: {
      promptEfficiency: 0.4,
      answerAccuracy: 0.4,
      creativityAndInnovation: 0.2,
    },
    questions: [
      {
        id: 1,
        type: 'System Design',
        question: 'Design the component architecture for a social media feed.',
        additionalConstraints: 'Focus on reusability and state management.',
      },
    ],
    candidateIds: [1, 3, 5, 8], // Priya, Amit, Vikram, Deepika
    createdAt: '2024-01-18T09:00:00Z',
  },
]

export const placeholderResults = {
  1: [ // Test 1: [1, 2, 3, 6, 9]
    { candidateId: 1, score: 85.5, submittedAt: '2024-01-20T10:30:00Z' }, // Priya
    { candidateId: 2, score: 92.3, submittedAt: '2024-01-20T11:15:00Z' }, // Rohan
    { candidateId: 3, score: 78.1, submittedAt: '2024-01-20T12:00:00Z' }, // Amit
    { candidateId: 6, score: 81.2, submittedAt: '2024-01-20T13:00:00Z' }, // Anjali
    // Arjun (9) has not submitted
  ],
  2: [ // Test 2: [2, 4, 5, 7, 10]
    { candidateId: 2, score: 88.7, submittedAt: '2024-01-21T09:00:00Z' }, // Rohan
    { candidateId: 4, score: 91.2, submittedAt: '2024-01-21T10:20:00Z' }, // Meera
    { candidateId: 5, score: 76.4, submittedAt: '2024-01-21T11:45:00Z' }, // Vikram
    { candidateId: 10, score: 89.0, submittedAt: '2024-01-21T12:15:00Z' }, // Neha
    // Sandeep (7) has not submitted
  ],
  3: [ // Test 3: [1, 3, 5, 8]
    { candidateId: 1, score: 94.0, submittedAt: '2024-01-22T10:00:00Z' }, // Priya
    { candidateId: 8, score: 82.5, submittedAt: '2024-01-22T10:30:00Z' }, // Deepika
    // Amit (3) and Vikram (5) have not submitted
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