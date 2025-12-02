'use client'

import { useState, useEffect, useRef } from 'react'

interface ProgressTrackerProps {
  tripId: string
  onComplete: () => void
}

interface ProgressData {
  status: 'running' | 'completed' | 'error'
  current_agent?: string
  current_step?: number
  total_steps?: number
  progress: number
  message: string
  estimated_time_remaining?: number
  debug?: {
    current_task?: number
    task_name?: string
    assigned_agent?: string
    agent_status?: 'waiting' | 'starting' | 'working' | 'complete'
    elapsed_time?: number
    remaining_time?: number
    all_tasks?: Array<{
      task: string
      agent: string
      status: string
    }>
  }
}

interface AgentStatus {
  id: string
  name: string
  icon: string
  status: 'complete' | 'working' | 'waiting'
  step: number
}

export default function ProgressTracker({ tripId, onComplete }: ProgressTrackerProps) {
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [elapsedTime, setElapsedTime] = useState(0)
  const eventSourceRef = useRef<EventSource | null>(null)
  const startTimeRef = useRef<number | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const statusRef = useRef<string | undefined>(undefined)

  // Update status ref whenever progress changes
  useEffect(() => {
    statusRef.current = progress?.status
  }, [progress?.status])

  // Timer effect - only runs while trip is in progress
  useEffect(() => {
    // Clear any existing interval first
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    // Only start timer if trip is running
    if (progress?.status === 'running') {
      // Initialize start time if not already set
      if (!startTimeRef.current) {
        startTimeRef.current = Date.now()
      }

      // Start interval to update elapsed time every second
      intervalRef.current = setInterval(() => {
        // Double-check status before updating (in case status changed between intervals)
        if (statusRef.current === 'running' && startTimeRef.current) {
          setElapsedTime(Math.floor((Date.now() - startTimeRef.current) / 1000))
        } else {
          // Status changed, stop the interval
          if (intervalRef.current) {
            clearInterval(intervalRef.current)
            intervalRef.current = null
          }
        }
      }, 1000)
    } else if (progress?.status === 'completed' || progress?.status === 'error') {
      // Stop timer when trip is completed or errored
      // Calculate final elapsed time once
      if (startTimeRef.current) {
        const finalTime = Math.floor((Date.now() - startTimeRef.current) / 1000)
        setElapsedTime(finalTime)
        // Reset start time to prevent any further updates
        startTimeRef.current = null
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [progress?.status])

  useEffect(() => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    // Fetch initial progress immediately
    const fetchInitialProgress = async (): Promise<ProgressData | null> => {
      try {
        const response = await fetch(`${apiUrl}/api/trips/${tripId}/progress`)
        if (response.ok) {
          const data: ProgressData = await response.json()
          setProgress(data)
          return data
        }
      } catch (err) {
        console.error('Error fetching initial progress:', err)
      }
      return null
    }
    
    fetchInitialProgress().then((data) => {
      // Log initial debug info if available
      if (data?.debug) {
        console.log('%c🚀 Trip Planning Started', 'color: #10b981; font-weight: bold; font-size: 14px;')
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        console.log(`Trip ID: ${tripId}`)
        console.log(`Status: ${data.status}`)
        if (data.debug.task_name) {
          console.log(`Initial Task: ${data.debug.task_name}`)
        }
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')
      }
    })
    
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
        
        // Log debug information to browser console
        if (data.debug) {
          console.log('%c🔍 Agent Debug Info', 'color: #3b82f6; font-weight: bold; font-size: 14px;')
          console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
          console.log(`📋 Task: ${data.debug.task_name || 'N/A'}`)
          console.log(`👤 Assigned to: ${data.debug.assigned_agent || 'N/A'}`)
          console.log(`📊 Status: ${data.debug.agent_status || 'N/A'}`)
          console.log(`📍 Step: ${data.current_step || 0}/${data.total_steps || 3}`)
          if (data.debug.elapsed_time !== undefined) {
            console.log(`⏱️  Elapsed: ${data.debug.elapsed_time}s | Remaining: ~${data.debug.remaining_time || 0}s`)
          }
          if (data.debug.all_tasks) {
            console.log('\n✅ All Tasks Status:')
            data.debug.all_tasks.forEach((task, idx) => {
              console.log(`  ${idx + 1}. ${task.task} → ${task.agent} [${task.status}]`)
            })
          }
          console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')
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
          
          // Log debug information to browser console
          if (data.debug) {
            console.log('%c🔍 Agent Debug Info (Polling)', 'color: #3b82f6; font-weight: bold; font-size: 14px;')
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            console.log(`📋 Task: ${data.debug.task_name || 'N/A'}`)
            console.log(`👤 Assigned to: ${data.debug.assigned_agent || 'N/A'}`)
            console.log(`📊 Status: ${data.debug.agent_status || 'N/A'}`)
            console.log(`📍 Step: ${data.current_step || 0}/${data.total_steps || 3}`)
            console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')
          }
          
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

  // Define agents with their details
  const agents: AgentStatus[] = [
    {
      id: 'trip_researcher',
      name: 'Trip Researcher',
      icon: '🔍',
      status: progress.current_step === undefined || progress.current_step === 0
        ? 'waiting'
        : progress.current_step > 1
        ? 'complete'
        : progress.current_agent === 'trip_researcher'
        ? 'working'
        : 'waiting',
      step: 1,
    },
    {
      id: 'trip_reviewer',
      name: 'Trip Reviewer',
      icon: '⭐',
      status: progress.current_step === undefined || progress.current_step < 2
        ? 'waiting'
        : progress.current_step > 2
        ? 'complete'
        : progress.current_agent === 'trip_reviewer'
        ? 'working'
        : 'waiting',
      step: 2,
    },
    {
      id: 'trip_planner',
      name: 'Trip Planner',
      icon: '📋',
      status: progress.current_step === undefined || progress.current_step < 3
        ? 'waiting'
        : progress.status === 'completed'
        ? 'complete'
        : progress.current_agent === 'trip_planner'
        ? 'working'
        : 'waiting',
      step: 3,
    },
  ]

  const currentStep = progress.current_step || 0
  const totalSteps = progress.total_steps || 3
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`
  }

  return (
    <div className="space-y-6">
      {/* Header with Step Indicator */}
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">
          Planning Your Trip...
        </h3>
        {progress.status === 'running' && (
          <p className="text-sm text-gray-600 mb-4">
            Step {currentStep}/{totalSteps}: {agents.find(a => a.step === currentStep)?.name || 'Processing'}...
          </p>
        )}
        {progress.status === 'completed' && (
          <div className="space-y-2">
            <div className="flex items-center justify-center space-x-2 text-green-600">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="font-medium">Trip plan generated successfully!</span>
            </div>
            <div className="flex items-center justify-center space-x-2 text-gray-600">
              <span>⭐</span>
              <span className="text-sm">Total time: {formatTime(elapsedTime)}</span>
            </div>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress.progress}%` }}
          ></div>
        </div>
      </div>

      {/* Current Step Info */}
      {progress.status === 'running' && progress.current_agent && (
        <div className="bg-blue-50 border-l-4 border-blue-500 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <span className="text-yellow-500 text-xl">⭐</span>
            <div>
              <p className="text-sm font-medium text-blue-900">
                Step {currentStep}/{totalSteps}: {agents.find(a => a.id === progress.current_agent)?.name}
              </p>
              <p className="text-xs text-blue-700 mt-1">{progress.message}</p>
            </div>
          </div>
          {progress.estimated_time_remaining && progress.estimated_time_remaining > 0 && (
            <div className="mt-2 flex items-center space-x-2 text-xs text-blue-600">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>Phase {currentStep}/{totalSteps} - {agents.find(a => a.step === currentStep)?.name.split(' ')[1] || 'Processing'} | Est. total: {Math.ceil((progress.estimated_time_remaining || 0) / 60)}-{Math.ceil((progress.estimated_time_remaining || 0) / 60) + 1} min</span>
            </div>
          )}
        </div>
      )}

      {/* Agent Status Cards */}
      <div className="space-y-3">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`rounded-lg p-4 border-2 transition-all duration-300 ${
              agent.status === 'complete'
                ? 'bg-green-50 border-green-200'
                : agent.status === 'working'
                ? 'bg-yellow-50 border-yellow-300 shadow-md'
                : 'bg-gray-50 border-gray-200 opacity-60'
            }`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{agent.icon}</span>
                <div>
                  <h4 className="font-medium text-gray-900">{agent.name}</h4>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {agent.status === 'complete' && (
                  <>
                    <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm font-medium text-green-700">Complete</span>
                  </>
                )}
                {agent.status === 'working' && (
                  <>
                    <div className="animate-spin">
                      <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <span className="text-sm font-medium text-yellow-700">Working...</span>
                  </>
                )}
                {agent.status === 'waiting' && (
                  <>
                    <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm font-medium text-gray-500">Waiting...</span>
                  </>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Completion Message */}
      {progress.status === 'completed' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <div className="flex items-center justify-center space-x-2 text-green-700">
            <span className="text-2xl">⭐</span>
            <span className="font-medium">Your trip plan is ready!</span>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}
    </div>
  )
}
