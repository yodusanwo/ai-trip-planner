'use client'

import { useState, useEffect } from 'react'

interface UsageStatsProps {
  clientId: string
}

interface UsageData {
  client_id: string
  trips_today: number
  trips_this_hour: number
  daily_cost: number
  cost_cap: number
  can_create_trip: boolean
  message?: string
}

export default function UsageStats({ clientId }: UsageStatsProps) {
  const [usage, setUsage] = useState<UsageData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/usage/${clientId}`)
        
        if (response.ok) {
          const data: UsageData = await response.json()
          setUsage(data)
        }
      } catch (err) {
        console.error('Error fetching usage stats:', err)
      } finally {
        setLoading(false)
      }
    }

    if (clientId) {
      fetchUsage()
      // Refresh every 30 seconds
      const interval = setInterval(fetchUsage, 30000)
      return () => clearInterval(interval)
    }
  }, [clientId])

  if (loading || !usage) {
    return null
  }

  const costPercentage = (usage.daily_cost / usage.cost_cap) * 100

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Usage Statistics</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600">Trips This Hour</p>
          <p className="text-2xl font-bold text-gray-900">{usage.trips_this_hour}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Trips Today</p>
          <p className="text-2xl font-bold text-gray-900">{usage.trips_today}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Daily Cost</p>
          <p className="text-2xl font-bold text-gray-900">${usage.daily_cost.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Cost Cap</p>
          <p className="text-2xl font-bold text-gray-900">${usage.cost_cap.toFixed(2)}</p>
        </div>
      </div>

      {/* Cost Progress Bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-gray-600">Daily Cost Usage</span>
          <span className="text-xs text-gray-600">{costPercentage.toFixed(1)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              costPercentage >= 80 ? 'bg-red-500' : costPercentage >= 60 ? 'bg-yellow-500' : 'bg-green-500'
            }`}
            style={{ width: `${Math.min(costPercentage, 100)}%` }}
          ></div>
        </div>
      </div>

      {/* Status Message */}
      {usage.message && (
        <div
          className={`p-3 rounded-lg ${
            usage.can_create_trip
              ? 'bg-blue-50 border border-blue-200 text-blue-700'
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}
        >
          <p className="text-sm">{usage.message}</p>
        </div>
      )}
    </div>
  )
}

