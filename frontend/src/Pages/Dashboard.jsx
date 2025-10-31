import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/placeholderData.js'
import Navbar from '@/components/navbar'

function RecruiterDashboardDummy() {
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
    <div className="min-h-screen text-white">
      <Navbar/>
      <div className="w-full text-white px-8 py-10 pt-24 flex flex-col max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] bg-clip-text text-transparent">
            Recruiter Dashboard
          </h1>
          <button
            onClick={() => navigate('/new-test')} // <-- FIX: Removed preventDefault/stopPropagation
            className="px-6 py-3 rounded-lg text-white font-medium bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] shadow-[0_0_20px_rgba(255,0,106,0.5)] hover:shadow-[0_0_30px_rgba(255,0,106,0.8)] transition-all duration-300 border border-white/10"
            style={{
              cursor: 'pointer',
              pointerEvents: 'auto',
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
          <div className="text-gray-400 text-center py-10 bg-white/5 rounded-2xl border border-white/10 backdrop-blur-lg">
            <h3 className="text-lg font-semibold text-white mb-2">No Tests Created Yet</h3>
            <p className="mb-4">Click the button above to get started.</p>
            <button
              onClick={() => navigate('/new-test')} // <-- FIX: Removed preventDefault/stopPropagation
              className="px-6 py-3 rounded-lg text-white font-medium bg-gradient-to-r from-[#ff6b00] via-[#ff2e2e] to-[#ff006a] shadow-[0_0_20px_rgba(255,0,106,0.5)] hover:shadow-[0_0_30px_rgba(255,0,106,0.8)] transition-all duration-300 border border-white/10"
              style={{
                cursor: 'pointer',
                pointerEvents: 'auto',
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
                onClick={() => navigate(`/test/${test.id}`)} // <-- FIX: Removed preventDefault/stopPropagation
                className="bg-white/10 rounded-2xl border border-white/10 p-6 backdrop-blur-lg shadow-[0_0_20px_rgba(255,255,255,0.1)] cursor-pointer hover:bg-white/20 transition-all duration-300"
                style={{
                  cursor: 'pointer',
                  pointerEvents: 'auto',
                  WebkitUserSelect: 'none',
                  userSelect: 'none'
                }}
              >
                <h3 className="text-xl font-semibold mb-2 text-white">{test.title}</h3>
                <div className="text-sm text-gray-300 mb-4">
                  {test.questions.length} question{test.questions.length !== 1 ? 's' : ''}
                </div>
                <div className="flex justify-between items-center text-xs text-gray-400">
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

export default RecruiterDashboardDummy
