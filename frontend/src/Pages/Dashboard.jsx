import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../utils/placeholderData'

function Dashboard() {
  const [tests, setTests] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadTests()
  }, [])

  const loadTests = async () => {
    try {
      setLoading(true)
      const data = await api.getTests()
      setTests(data)
    } catch (error) {
      console.error('Error loading tests:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-[#ff672f] to-[#ff4500] bg-clip-text text-transparent">
            Recruiter Dashboard
          </h1>
          <button
            onClick={(e) => {
              e.preventDefault()
              e.stopPropagation()
              navigate('/new-test')
            }}
            className="px-6 py-3 bg-gradient-to-r from-[#ff672f] to-[#ff4500] text-white font-semibold rounded-lg hover:opacity-90 transition-opacity shadow-lg"
            style={{
              cursor: 'pointer',
              pointerEvents: 'auto',
              backgroundImage: 'linear-gradient(to right, #ff672f, #ff4500)',
              WebkitUserSelect: 'none',
              userSelect: 'none'
            }}
          >
            + Create New Test
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-gray-400">Loading tests...</div>
          </div>
        ) : tests.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-gray-400 text-lg mb-4">No tests created yet</div>
            <button
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                navigate('/new-test')
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
              Create Your First Test
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tests.map((test) => (
              <div
                key={test.id}
                onClick={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  navigate(`/test/${test.id}`)
                }}
                className="bg-[#1a1a1a] border border-gray-800 rounded-lg p-6 cursor-pointer hover:border-[#ff672f] transition-colors"
                style={{
                  cursor: 'pointer',
                  pointerEvents: 'auto',
                  WebkitUserSelect: 'none',
                  userSelect: 'none'
                }}
              >
                <h3 className="text-xl font-semibold mb-2 text-white">{test.title}</h3>
                <div className="text-sm text-gray-400 mb-4">
                  {test.questions.length} question{test.questions.length !== 1 ? 's' : ''}
                </div>
                <div className="flex justify-between items-center text-xs text-gray-500">
                  <span>{test.candidateIds.length} candidate{test.candidateIds.length !== 1 ? 's' : ''}</span>
                  <span>Budget: {test.promptBudget.toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard


