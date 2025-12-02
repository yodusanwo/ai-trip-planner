'use client'

import { useState, useEffect } from 'react'
import TripForm, { TripDetails } from '@/components/TripForm'
import ProgressTracker from '@/components/ProgressTracker'
import TripResult from '@/components/TripResult'
import UsageStats from '@/components/UsageStats'
import WelcomeSection from '@/components/WelcomeSection'
import PlanningProgressPlaceholder from '@/components/PlanningProgressPlaceholder'

export default function Home() {
  const [tripId, setTripId] = useState<string | null>(null)
  const [clientId, setClientId] = useState<string | null>(null)
  const [showResult, setShowResult] = useState(false)
  const [tripDetails, setTripDetails] = useState<TripDetails | null>(null)

  // Generate client ID on mount
  useEffect(() => {
    const storedClientId = localStorage.getItem('trip_planner_client_id')
    if (storedClientId) {
      setClientId(storedClientId)
    } else {
      const newClientId = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      localStorage.setItem('trip_planner_client_id', newClientId)
      setClientId(newClientId)
    }
  }, [])

  const handleTripCreated = (newTripId: string, newClientId: string, details: TripDetails) => {
    setTripId(newTripId)
    setClientId(newClientId)
    setTripDetails(details)
    setShowResult(false)
  }

  const handleTripComplete = () => {
    setShowResult(true)
  }

  const handleStartNewTrip = () => {
    setTripId(null)
    setTripDetails(null)
    setShowResult(false)
    // Scroll to top to show welcome section
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            ✈️ AI Trip Planner
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Plan your perfect trip with AI-powered research and recommendations
          </p>
          <p className="text-sm text-gray-500">
            Created by <span className="font-semibold">Zora Digital</span> - A showcase of AI Agent capabilities
          </p>
        </header>

        {/* Usage Stats */}
        {clientId && <UsageStats clientId={clientId} />}

        {/* Welcome Section - Show when no active trip */}
        {!tripId && !showResult && <WelcomeSection />}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Trip Form */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
              Plan Your Trip
            </h2>
            <TripForm 
              clientId={clientId} 
              onTripCreated={handleTripCreated}
            />
          </div>

          {/* Progress Tracker or Placeholder */}
          {tripId ? (
            <div className="bg-white rounded-lg shadow-lg p-6" id="progress-anchor">
              <h2 className="text-2xl font-semibold mb-4 text-gray-800">
                Planning Progress
              </h2>
              <ProgressTracker 
                tripId={tripId}
                onComplete={handleTripComplete}
                tripDetails={tripDetails}
              />
            </div>
          ) : (
            <PlanningProgressPlaceholder />
          )}
        </div>

        {/* Trip Result */}
        {showResult && tripId && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="mb-4 flex justify-end">
              <button
                onClick={handleStartNewTrip}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold shadow-md hover:shadow-lg"
              >
                ✨ Plan Another Trip
              </button>
            </div>
            <TripResult tripId={tripId} />
          </div>
        )}

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-600 border-t pt-6">
          <div className="flex flex-col items-center space-y-2">
            <p className="text-sm">
              Built with <span className="font-semibold">CrewAI</span> and <span className="font-semibold">Next.js</span>
            </p>
            <p className="text-xs">
              © 2025 Zora Digital
            </p>
          </div>
        </footer>
      </div>
    </main>
  )
}

