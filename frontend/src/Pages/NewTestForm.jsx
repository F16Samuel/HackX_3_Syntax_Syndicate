import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../utils/placeholderData'

const QUESTION_TYPES = [
  'Data Structures & Algorithms',
  'System Design',
  'Cloud Computing',
]

function NewTestForm() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [candidates, setCandidates] = useState([])
  
  const [formData, setFormData] = useState({
    title: '',
    promptBudget: '',
    rubrics: {
      promptEfficiency: 0.3,
      answerAccuracy: 0.5,
      creativityAndInnovation: 0.2,
    },
    questions: [
      {
        id: Date.now(),
        type: 'Data Structures & Algorithms',
        question: '',
        additionalConstraints: '',
      },
    ],
    candidateIds: [],
  })

  useEffect(() => {
    loadCandidates()
  }, [])

  const loadCandidates = async () => {
    try {
      const data = await api.getCandidates()
      setCandidates(data)
    } catch (error) {
      console.error('Error loading candidates:', error)
    }
  }

  const handleRubricChange = (rubric, value) => {
    const numValue = parseFloat(value)
    if (numValue >= 0 && numValue <= 1) {
      setFormData((prev) => ({
        ...prev,
        rubrics: {
          ...prev.rubrics,
          [rubric]: numValue,
        },
      }))
    }
  }

  const addQuestion = () => {
    setFormData((prev) => ({
      ...prev,
      questions: [
        ...prev.questions,
        {
          id: Date.now(),
          type: 'Data Structures & Algorithms',
          question: '',
          additionalConstraints: '',
        },
      ],
    }))
  }

  const removeQuestion = (questionId) => {
    setFormData((prev) => ({
      ...prev,
      questions: prev.questions.filter(q => q.id !== questionId),
    }))
  }

  const updateQuestion = (questionId, field, value) => {
    setFormData((prev) => ({
      ...prev,
      questions: prev.questions.map(q =>
        q.id === questionId ? { ...q, [field]: value } : q
      ),
    }))
  }

  const toggleCandidate = (candidateId) => {
    setFormData((prev) => ({
      ...prev,
      candidateIds: prev.candidateIds.includes(candidateId)
        ? prev.candidateIds.filter(id => id !== candidateId)
        : [...prev.candidateIds, candidateId],
    }))
  }

  const validateForm = () => {
    if (!formData.title.trim()) {
      alert('Please enter a test title')
      return false
    }
    if (!formData.promptBudget || parseFloat(formData.promptBudget) <= 0) {
      alert('Please enter a valid prompt budget')
      return false
    }
    const totalWeight = Object.values(formData.rubrics).reduce((sum, val) => sum + val, 0)
    if (Math.abs(totalWeight - 1) > 0.01) {
      alert('Rubric weightages must sum to 1')
      return false
    }
    if (formData.questions.some(q => !q.question.trim())) {
      alert('Please fill in all questions')
      return false
    }
    if (formData.candidateIds.length === 0) {
      alert('Please select at least one candidate')
      return false
    }
    return true
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (!validateForm()) return

    if (loading) return // Prevent multiple submissions

    try {
      setLoading(true)
      const testData = {
        ...formData,
        promptBudget: parseFloat(formData.promptBudget),
      }
      const newTest = await api.createTest(testData)
      navigate(`/test/${newTest.id}`)
    } catch (error) {
      console.error('Error creating test:', error)
      alert('Failed to create test. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const totalWeight = Object.values(formData.rubrics).reduce((sum, val) => sum + val, 0)

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center mb-8">
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigate('/')
            }}
            className="mr-4 text-gray-400 hover:text-white"
          >
            ← Back
          </button>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-[#ff672f] to-[#ff4500] bg-clip-text text-transparent">
            Create New Test
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Test Title */}
          <div className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6">
            <label className="block text-lg font-semibold mb-2">Test Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
              className="w-full px-4 py-2 bg-black border border-gray-700 rounded-lg text-white focus:border-[#ff672f] focus:outline-none"
              placeholder="Enter test title"
              required
            />
          </div>

          {/* Prompt Budget */}
          <div className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6">
            <label className="block text-lg font-semibold mb-2">Prompt Budget</label>
            <input
              type="number"
              value={formData.promptBudget}
              onChange={(e) => setFormData((prev) => ({ ...prev, promptBudget: e.target.value }))}
              className="w-full px-4 py-2 bg-black border border-gray-700 rounded-lg text-white focus:border-[#ff672f] focus:outline-none"
              placeholder="Enter prompt budget"
              min="1"
              required
            />
          </div>

          {/* Rubrics */}
          <div className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <label className="block text-lg font-semibold">Marking Rubrics Weightage</label>
              <span className={`text-sm ${Math.abs(totalWeight - 1) < 0.01 ? 'text-green-400' : 'text-red-400'}`}>
                Total: {totalWeight.toFixed(2)} / 1.00
              </span>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-300 mb-2">Prompt Efficiency</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={formData.rubrics.promptEfficiency}
                  onChange={(e) => handleRubricChange('promptEfficiency', e.target.value)}
                  className="w-full px-4 py-2 bg-black border border-gray-700 rounded-lg text-white focus:border-[#ff672f] focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-2">Answer Accuracy</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={formData.rubrics.answerAccuracy}
                  onChange={(e) => handleRubricChange('answerAccuracy', e.target.value)}
                  className="w-full px-4 py-2 bg-black border border-gray-700 rounded-lg text-white focus:border-[#ff672f] focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-2">Creativity and Innovation</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={formData.rubrics.creativityAndInnovation}
                  onChange={(e) => handleRubricChange('creativityAndInnovation', e.target.value)}
                  className="w-full px-4 py-2 bg-black border border-gray-700 rounded-lg text-white focus:border-[#ff672f] focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Questions */}
          <div className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <label className="block text-lg font-semibold">Questions</label>
              <button
                type="button"
                onClick={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  addQuestion()
                }}
                className="px-4 py-2 bg-gradient-to-r from-[#ff672f] to-[#ff4500] text-white text-sm font-semibold rounded-lg hover:opacity-90 transition-opacity"
                style={{
                  cursor: 'pointer',
                  pointerEvents: 'auto',
                  backgroundImage: 'linear-gradient(to right, #ff672f, #ff4500)',
                  WebkitUserSelect: 'none',
                  userSelect: 'none'
                }}
              >
                + Add Question
              </button>
            </div>
            <div className="space-y-6">
              {formData.questions.map((question, index) => (
                <div key={question.id} className="border border-gray-700 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-sm font-semibold text-gray-300">Question {index + 1}</span>
                    {formData.questions.length > 1 && (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault()
                          e.stopPropagation()
                          removeQuestion(question.id)
                        }}
                        className="text-red-400 hover:text-red-300 text-sm"
                      >
                        Remove
                      </button>
                    )}
                  </div>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm text-gray-300 mb-2">Question Type</label>
                      <select
                        value={question.type}
                        onChange={(e) => updateQuestion(question.id, 'type', e.target.value)}
                        className="w-full px-4 py-2 bg-black border border-gray-700 rounded-lg text-white focus:border-[#ff672f] focus:outline-none"
                      >
                        {QUESTION_TYPES.map(type => (
                          <option key={type} value={type}>{type}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm text-gray-300 mb-2">Question</label>
                      <textarea
                        value={question.question}
                        onChange={(e) => updateQuestion(question.id, 'question', e.target.value)}
                        className="w-full px-4 py-2 bg-black border border-gray-700 rounded-lg text-white focus:border-[#ff672f] focus:outline-none"
                        rows="3"
                        placeholder="Enter the question"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-300 mb-2">Additional Constraints</label>
                      <textarea
                        value={question.additionalConstraints}
                        onChange={(e) => updateQuestion(question.id, 'additionalConstraints', e.target.value)}
                        className="w-full px-4 py-2 bg-black border border-gray-700 rounded-lg text-white focus:border-[#ff672f] focus:outline-none"
                        rows="2"
                        placeholder="Enter any additional constraints"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Candidates */}
          <div className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6">
            <label className="block text-lg font-semibold mb-4">Select Candidates</label>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {candidates.map((candidate) => (
                <label
                  key={candidate.id}
                  className="flex items-center p-3 bg-black border border-gray-700 rounded-lg cursor-pointer hover:border-[#ff672f] transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={formData.candidateIds.includes(candidate.id)}
                    onChange={() => toggleCandidate(candidate.id)}
                    className="mr-3 w-4 h-4 text-[#ff672f] bg-black border-gray-700 rounded focus:ring-[#ff672f]"
                  />
                  <div>
                    <div className="text-white">{candidate.name}</div>
                    <div className="text-sm text-gray-400">{candidate.email}</div>
                  </div>
                </label>
              ))}
            </div>
            {formData.candidateIds.length > 0 && (
              <div className="mt-4 text-sm text-gray-400">
                {formData.candidateIds.length} candidate{formData.candidateIds.length !== 1 ? 's' : ''} selected
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                navigate('/')
              }}
              className="px-6 py-3 bg-gray-800 text-white font-semibold rounded-lg hover:bg-gray-700 transition-colors"
              style={{
                cursor: 'pointer',
                pointerEvents: 'auto',
                WebkitUserSelect: 'none',
                userSelect: 'none'
              }}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-3 bg-gradient-to-r from-[#ff672f] to-[#ff4500] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                cursor: loading ? 'not-allowed' : 'pointer',
                pointerEvents: loading ? 'none' : 'auto',
                backgroundImage: 'linear-gradient(to right, #ff672f, #ff4500)',
                WebkitUserSelect: 'none',
                userSelect: 'none'
              }}
            >
              {loading ? 'Creating...' : 'Create Test'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default NewTestForm


