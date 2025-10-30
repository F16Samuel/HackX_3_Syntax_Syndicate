import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api, placeholderCandidates } from '../utils/placeholderData'

function TestResults() {
  const { testId } = useParams()
  const navigate = useNavigate()
  const [test, setTest] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showAddCandidatesModal, setShowAddCandidatesModal] = useState(false)
  const [selectedCandidateIds, setSelectedCandidateIds] = useState([])

  useEffect(() => {
    loadTestData()
  }, [testId])

  const loadTestData = async () => {
    try {
      setLoading(true)
      const [tests, resultsData] = await Promise.all([
        api.getTests(),
        api.getTestResults(parseInt(testId)),
      ])
      const foundTest = tests.find(t => t.id === parseInt(testId))
      setTest(foundTest)
      setResults(resultsData)
      if (foundTest) {
        setSelectedCandidateIds(foundTest.candidateIds)
      }
    } catch (error) {
      console.error('Error loading test data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getCandidateName = (candidateId) => {
    const candidate = placeholderCandidates.find(c => c.id === candidateId)
    return candidate ? candidate.name : `Candidate ${candidateId}`
  }

  const getCandidateEmail = (candidateId) => {
    const candidate = placeholderCandidates.find(c => c.id === candidateId)
    return candidate ? candidate.email : 'N/A'
  }

  const sortedResults = [...results].sort((a, b) => b.score - a.score)

  const handleAddCandidates = async () => {
    if (!test) return
    
    try {
      const updatedCandidateIds = [...new Set([...test.candidateIds, ...selectedCandidateIds])]
      await api.updateTest(test.id, { candidateIds: updatedCandidateIds })
      setTest((prev) => prev ? { ...prev, candidateIds: updatedCandidateIds } : null)
      setShowAddCandidatesModal(false)
      setSelectedCandidateIds([])
      alert('Candidates added successfully!')
    } catch (error) {
      console.error('Error adding candidates:', error)
      alert('Failed to add candidates. Please try again.')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-gray-400">Loading test results...</div>
      </div>
    )
  }

  if (!test) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-400 mb-4">Test not found</div>
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigate('/')
            }}
            className="px-6 py-3 bg-gradient-to-r from-[#ff672f] to-[#ff4500] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity"
            style={{
              cursor: 'pointer',
              pointerEvents: 'auto',
              backgroundImage: 'linear-gradient(to right, #ff672f, #ff4500)',
              WebkitUserSelect: 'none',
              userSelect: 'none'
            }}
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
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
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-[#ff672f] to-[#ff4500] bg-clip-text text-transparent">
                {test.title}
              </h1>
              <div className="text-sm text-gray-400 mt-1">
                {test.candidateIds.length} candidate{test.candidateIds.length !== 1 ? 's' : ''} • {results.length} attempt{results.length !== 1 ? 's' : ''}
              </div>
            </div>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                setShowAddCandidatesModal(true)
              }}
              className="px-4 py-2 bg-gray-800 text-white font-semibold rounded-lg hover:bg-gray-700 transition-colors"
              style={{
                cursor: 'pointer',
                pointerEvents: 'auto',
                WebkitUserSelect: 'none',
                userSelect: 'none'
              }}
            >
              + Add Candidates
            </button>
            <button
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                setShowEditModal(true)
              }}
              className="px-4 py-2 bg-gradient-to-r from-[#ff672f] to-[#ff4500] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity"
              style={{
                cursor: 'pointer',
                pointerEvents: 'auto',
                backgroundImage: 'linear-gradient(to right, #ff672f, #ff4500)',
                WebkitUserSelect: 'none',
                userSelect: 'none'
              }}
            >
              Edit Test
            </button>
          </div>
        </div>

        {/* Leaderboard */}
        <div className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6 mb-6">
          <h2 className="text-2xl font-semibold mb-6">Leaderboard</h2>
          {results.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No submissions yet. Candidates will appear here once they complete the test.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="text-left py-3 px-4 text-gray-300 font-semibold">Rank</th>
                    <th className="text-left py-3 px-4 text-gray-300 font-semibold">Candidate</th>
                    <th className="text-left py-3 px-4 text-gray-300 font-semibold">Email</th>
                    <th className="text-right py-3 px-4 text-gray-300 font-semibold">Score</th>
                    <th className="text-left py-3 px-4 text-gray-300 font-semibold">Submitted</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedResults.map((result, index) => (
                    <tr key={result.candidateId} className="border-b border-gray-800 hover:bg-gray-900 transition-colors">
                      <td className="py-4 px-4">
                        <div className="flex items-center">
                          {index === 0 && <span className="text-2xl mr-2">🥇</span>}
                          {index === 1 && <span className="text-2xl mr-2">🥈</span>}
                          {index === 2 && <span className="text-2xl mr-2">🥉</span>}
                          <span className="font-semibold">{index + 1}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 font-medium">{getCandidateName(result.candidateId)}</td>
                      <td className="py-4 px-4 text-gray-400">{getCandidateEmail(result.candidateId)}</td>
                      <td className="py-4 px-4 text-right">
                        <span className="text-xl font-bold bg-gradient-to-r from-[#ff672f] to-[#ff4500] bg-clip-text text-transparent">
                          {result.score.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-400">
                        {new Date(result.submittedAt).toLocaleDateString()} {new Date(result.submittedAt).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Test Details */}
        <div className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6">
          <h2 className="text-2xl font-semibold mb-4">Test Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="text-sm text-gray-400 mb-1">Prompt Budget</div>
              <div className="text-lg font-semibold">{test.promptBudget.toLocaleString()}</div>
            </div>
            <div>
              <div className="text-sm text-gray-400 mb-1">Rubrics Weightage</div>
              <div className="space-y-1">
                <div className="text-sm">Prompt Efficiency: {(test.rubrics.promptEfficiency * 100).toFixed(0)}%</div>
                <div className="text-sm">Answer Accuracy: {(test.rubrics.answerAccuracy * 100).toFixed(0)}%</div>
                <div className="text-sm">Creativity & Innovation: {(test.rubrics.creativityAndInnovation * 100).toFixed(0)}%</div>
              </div>
            </div>
          </div>
          <div className="mt-6">
            <div className="text-sm text-gray-400 mb-2">Questions ({test.questions.length})</div>
            <div className="space-y-3">
              {test.questions.map((q, idx) => (
                <div key={idx} className="bg-black border border-gray-700 rounded-lg p-4">
                  <div className="text-xs text-gray-400 mb-1">{q.type}</div>
                  <div className="font-medium mb-2">{q.question}</div>
                  {q.additionalConstraints && (
                    <div className="text-sm text-gray-400">{q.additionalConstraints}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Add Candidates Modal */}
        {showAddCandidatesModal && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                e.preventDefault()
                e.stopPropagation()
                setShowAddCandidatesModal(false)
                setSelectedCandidateIds([])
              }
            }}
          >
            <div 
              className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-2xl font-semibold">Add Candidates</h3>
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    setShowAddCandidatesModal(false)
                    setSelectedCandidateIds([])
                  }}
                  className="text-gray-400 hover:text-white"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-2 mb-6 max-h-64 overflow-y-auto">
                {placeholderCandidates
                  .filter(c => !test.candidateIds.includes(c.id))
                  .map((candidate) => (
                    <label
                      key={candidate.id}
                      className="flex items-center p-3 bg-black border border-gray-700 rounded-lg cursor-pointer hover:border-[#ff672f] transition-colors"
                    >
                      <input
                        type="checkbox"
                        checked={selectedCandidateIds.includes(candidate.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCandidateIds([...selectedCandidateIds, candidate.id])
                          } else {
                            setSelectedCandidateIds(selectedCandidateIds.filter(id => id !== candidate.id))
                          }
                        }}
                        className="mr-3 w-4 h-4 text-[#ff672f] bg-black border-gray-700 rounded focus:ring-[#ff672f]"
                      />
                      <div>
                        <div className="text-white">{candidate.name}</div>
                        <div className="text-sm text-gray-400">{candidate.email}</div>
                      </div>
                    </label>
                  ))}
              </div>
              {placeholderCandidates.filter(c => !test.candidateIds.includes(c.id)).length === 0 && (
                <div className="text-center py-4 text-gray-400">All candidates are already added</div>
              )}
              <div className="flex justify-end space-x-3">
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    setShowAddCandidatesModal(false)
                    setSelectedCandidateIds([])
                  }}
                  className="px-4 py-2 bg-gray-800 text-white font-semibold rounded-lg hover:bg-gray-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    handleAddCandidates()
                  }}
                  disabled={selectedCandidateIds.length === 0}
                  className="px-4 py-2 bg-gradient-to-r from-[#ff672f] to-[#ff4500] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                  style={{
                    cursor: selectedCandidateIds.length === 0 ? 'not-allowed' : 'pointer',
                    pointerEvents: selectedCandidateIds.length === 0 ? 'none' : 'auto',
                    backgroundImage: 'linear-gradient(to right, #ff672f, #ff4500)',
                    WebkitUserSelect: 'none',
                    userSelect: 'none'
                  }}
                >
                  Add Selected
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Edit Test Modal */}
        {showEditModal && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
            onClick={(e) => {
              if (e.target === e.currentTarget) {
                e.preventDefault()
                e.stopPropagation()
                setShowEditModal(false)
              }
            }}
          >
            <div 
              className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-2xl font-semibold">Edit Test</h3>
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    setShowEditModal(false)
                  }}
                  className="text-gray-400 hover:text-white"
                >
                  ✕
                </button>
              </div>
              <div className="text-gray-400 mb-4">
                Note: Edit functionality is a placeholder. Replace with actual edit form when backend is ready.
              </div>
              <button
                onClick={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  setShowEditModal(false)
                }}
                className="w-full px-4 py-2 bg-gradient-to-r from-[#ff672f] to-[#ff4500] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity"
                style={{
                  cursor: 'pointer',
                  pointerEvents: 'auto',
                  backgroundImage: 'linear-gradient(to right, #ff672f, #ff4500)',
                  WebkitUserSelect: 'none',
                  userSelect: 'none'
                }}
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default TestResults


