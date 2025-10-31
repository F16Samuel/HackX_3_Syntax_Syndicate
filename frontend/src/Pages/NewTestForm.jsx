import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/placeholderData'
import Navbar from '@/components/navbar'


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
      alert('Please enter a test title') // Note: alert() might not work in iframe
      return false
    }
    if (!formData.promptBudget || parseFloat(formData.promptBudget) <= 0) {
      alert('Please enter a valid prompt budget') // Note: alert() might not work in iframe
      return false
    }
    const totalWeight = Object.values(formData.rubrics).reduce((sum, val) => sum + val, 0)
    if (Math.abs(totalWeight - 1) > 0.01) {
      alert('Rubric weightages must sum to 1') // Note: alert() might not work in iframe
      return false
    }
    if (formData.questions.some(q => !q.question.trim())) {
      alert('Please fill in all questions') // Note: alert() might not work in iframe
      return false
    }
    if (formData.candidateIds.length === 0) {
      alert('Please select at least one candidate') // Note: alert() might not work in iframe
      return false
    }
    return true
  }

  // This is a form submission, so preventDefault IS correct here.
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
      alert('Failed to create test. Please try again.') // Note: alert() might not work in iframe
    } finally {
      setLoading(false)
    }
  }

  const totalWeight = Object.values(formData.rubrics).reduce((sum, val) => sum + val, 0)

  return (
    <div className="min-h-screen text-white">
      <Navbar/>
      <div className="w-full text-white px-8 py-10 pt-24 flex flex-col max-w-4xl mx-auto">
        <div className="flex items-center mb-8">
          <button
            onClick={() => navigate('/recruiter-dummy')} // <-- FIX: Removed preventDefault/stopPropagation
            className="mr-4 text-gray-300 hover:text-white"
          >
            ← Back
          </button>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] bg-clip-text text-transparent">
            Create New Test
          </h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Test Title */}
          <div className="bg-white/10 rounded-2xl border border-white/10 p-6 backdrop-blur-lg shadow-[0_0_20px_rgba(255,255,255,0.1)]">
            <label className="block text-lg font-semibold mb-2">Test Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
              className="w-full bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#ff6b00]/50 backdrop-blur-sm transition"
              placeholder="Enter test title"
              required
            />
          </div>

          {/* Prompt Budget */}
          <div className="bg-white/10 rounded-2xl border border-white/10 p-6 backdrop-blur-lg shadow-[0_0_20px_rgba(255,255,255,0.1)]">
            <label className="block text-lg font-semibold mb-2">Prompt Budget</label>
            <input
              type="number"
              value={formData.promptBudget}
              onChange={(e) => setFormData((prev) => ({ ...prev, promptBudget: e.target.value }))}
              className="w-full bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#ff6b00]/50 backdrop-blur-sm transition"
              placeholder="Enter prompt budget"
              min="1"
              required
            />
          </div>

          {/* Rubrics */}
          <div className="bg-white/10 rounded-2xl border border-white/10 p-6 backdrop-blur-lg shadow-[0_0_20px_rgba(255,255,255,0.1)]">
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
                  className="w-full bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#ff6b00]/50 backdrop-blur-sm transition"
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
                  className="w-full bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#ff6b00]/50 backdrop-blur-sm transition"
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
                  className="w-full bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#ff6b00]/50 backdrop-blur-sm transition"
                />
              </div>
            </div>
          </div>

          {/* Questions */}
          <div className="bg-white/10 rounded-2xl border border-white/10 p-6 backdrop-blur-lg shadow-[0_0_20px_rgba(255,255,255,0.1)]">
            <div className="flex justify-between items-center mb-4">
              <label className="block text-lg font-semibold">Questions</label>
              <button
                type="button"
                onClick={addQuestion} // <-- FIX: Simplified
                className="px-5 py-2 rounded-lg text-white text-sm font-medium bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] shadow-[0_0_10px_rgba(255,0,106,0.4)] hover:shadow-[0_0_20px_rgba(255,0,106,0.7)] transition-all duration-300 border border-white/10"
                style={{
                  cursor: 'pointer',
                  pointerEvents: 'auto',
                  WebkitUserSelect: 'none',
                  userSelect: 'none'
                }}
              >
                + Add Question
              </button>
            </div>
            <div className="space-y-6">
              {formData.questions.map((question, index) => (
                <div key={question.id} className="border border-white/20 rounded-xl p-4">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-sm font-semibold text-gray-300">Question {index + 1}</span>
                    {formData.questions.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeQuestion(question.id)} // <-- FIX: Simplified
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
                        className="w-full bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-gray-200 focus:outline-none focus:ring-2 focus:ring-[#ff6b00]/50 backdrop-blur-sm transition appearance-none"
                      >
                        {QUESTION_TYPES.map(type => (
                          <option key={type} value={type} className="bg-black text-white">{type}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm text-gray-300 mb-2">Question</label>
                      <textarea
                        value={question.question}
                        onChange={(e) => updateQuestion(question.id, 'question', e.target.value)}
                        className="w-full bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#ff6b00]/50 backdrop-blur-sm transition"
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
                        className="w-full bg-white/10 border border-white/10 rounded-xl px-4 py-3 text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#ff6b00]/50 backdrop-blur-sm transition"
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
          <div className="bg-white/10 rounded-2xl border border-white/10 p-6 backdrop-blur-lg shadow-[0_0_20px_rgba(255,255,255,0.1)]">
            <label className="block text-lg font-semibold mb-4">Select Candidates</label>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {candidates.map((candidate) => (
                <label
                  key={candidate.id}
                  className="flex items-center p-3 bg-white/5 border border-white/10 rounded-xl cursor-pointer hover:bg-white/10 transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={formData.candidateIds.includes(candidate.id)}
                    onChange={() => toggleCandidate(candidate.id)}
                    className="mr-3 w-4 h-4 text-[#ff2e2e] bg-white/10 border-white/20 rounded focus:ring-2 focus:ring-[#ff2e2e]"
                  />
                  <div>
                    <div className="text-white">{candidate.name}</div>
                    <div className="text-sm text-gray-300">{candidate.email}</div>
                  </div>
                </label>
              ))}
            </div>
            {formData.candidateIds.length > 0 && (
              <div className="mt-4 text-sm text-gray-300">
                {formData.candidateIds.length} candidate{formData.candidateIds.length !== 1 ? 's' : ''} selected
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/recruiter-dummy')} // <-- FIX: Removed preventDefault/stopPropagation
              className="px-6 py-3 rounded-lg text-white font-medium bg-white/10 hover:bg-white/20 border border-white/10 transition-all duration-300"
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
              className="px-6 py-3 rounded-lg text-white font-medium bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] shadow-[0_0_20px_rgba(255,0,106,0.5)] hover:shadow-[0_0_30px_rgba(255,0,106,0.8)] transition-all duration-300 border border-white/10 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{
                cursor: loading ? 'not-allowed' : 'pointer',
                pointerEvents: loading ? 'none' : 'auto',
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
