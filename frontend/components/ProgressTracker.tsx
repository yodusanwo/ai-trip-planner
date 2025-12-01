'use client'

import { useState, useEffect, useRef } from 'react'

interface ProgressTrackerProps {
  tripId: string
  onComplete: () => void
}

interface ProgressData {
  status: 'running' | 'completed' | 'error'
  current_agent?: string
  progress: number
  message: string
  estimated_time_remaining?: number
}

export default function ProgressTracker({ tripId, onComplete }: ProgressTrackerProps) {
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    // Fetch initial progress immediately
    const fetchInitialProgress = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/trips/${tripId}/progress`)
        if (response.ok) {
          const data: ProgressData = await response.json()
          setProgress(data)
        }
      } catch (err) {
        console.error('Error fetching initial progress:', err)
      }
    }
    
    fetchInitialProgress()
    
    // Create EventSource for SSE
    const eventSource = new EventSource(`${apiUrl}/api/trips/${tripId}/progress/stream`)
    eventSourceRef.current = eventSource

    eventSource.onmessage = (event) => {
      try {
        const data: ProgressData = JSON.parse(event.data)
        
        // Ignore connection messages
        if (data.status === 'connected') {
          return
        }
        
        setProgress(data)
        setError(null)

        if (data.status === 'completed') {
          eventSource.close()
          setTimeout(() => onComplete(), 500)
        } else if (data.status === 'error') {
          eventSource.close()
          setError(data.message)
        }
      } catch (err) {
        console.error('Error parsing progress data:', err)
      }
    }

    eventSource.onerror = (error) => {
      console.error('SSE error:', error)
      // Fallback to polling if SSE fails
      eventSource.close()
      pollProgress()
    }

    return () => {
      eventSource.close()
    }
  }, [tripId, onComplete])

  const pollProgress = async () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`${apiUrl}/api/trips/${tripId}/progress`)
        if (response.ok) {
          const data: ProgressData = await response.json()
          setProgress(data)
          
          if (data.status === 'completed') {
            clearInterval(interval)
            onComplete()
          } else if (data.status === 'error') {
            clearInterval(interval)
            setError(data.message)
          }
        }
      } catch (err) {
        console.error('Error polling progress:', err)
      }
    }, 2000)

    return () => clearInterval(interval)
  }

  if (!progress) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-3 text-gray-600">Loading progress...</span>
      </div>
    )
  }

  const agentNames: Record<string, string> = {
    trip_researcher: 'Research Agent',
    trip_reviewer: 'Review Agent',
    trip_planner: 'Planning Agent',
  }

  return (
    <div className="space-y-4">
      {/* Progress Bar */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">
            {progress.status === 'completed' ? 'Complete!' : 'In Progress...'}
          </span>
          <span className="text-sm text-gray-500">{progress.progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-primary-600 h-3 rounded-full transition-all duration-500"
            style={{ width: `${progress.progress}%` }}
          ></div>
        </div>
      </div>

      {/* Current Agent */}
      {progress.current_agent && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm font-medium text-blue-900">
            Current Step: {agentNames[progress.current_agent] || progress.current_agent}
          </p>
        </div>
      )}

      {/* Status Message */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <p className="text-sm text-gray-700">{progress.message}</p>
      </div>

      {/* Estimated Time */}
      {progress.estimated_time_remaining && progress.estimated_time_remaining > 0 && (
        <div className="text-sm text-gray-500">
          Estimated time remaining: ~{Math.ceil(progress.estimated_time_remaining / 60)} minutes
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Status Badge */}
      <div className="flex items-center space-x-2">
        <div
          className={`w-3 h-3 rounded-full ${
            progress.status === 'completed'
              ? 'bg-green-500'
              : progress.status === 'error'
              ? 'bg-red-500'
              : 'bg-blue-500 animate-pulse'
          }`}
        ></div>
        <span className="text-sm font-medium text-gray-700 capitalize">
          {progress.status}
        </span>
      </div>
    </div>
  )
}

