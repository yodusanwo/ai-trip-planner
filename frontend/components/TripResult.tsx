'use client'

import { useState, useEffect } from 'react'

interface TripResultProps {
  tripId: string
}

export default function TripResult({ tripId }: TripResultProps) {
  const [htmlContent, setHtmlContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchResult = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/trips/${tripId}/result`)

        if (response.status === 202) {
          // Still in progress, retry after a delay
          setTimeout(fetchResult, 2000)
          return
        }

        if (!response.ok) {
          throw new Error('Failed to fetch trip result')
        }

        const data = await response.json()
        setHtmlContent(data.html_content)
        setLoading(false)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load trip result')
        setLoading(false)
      }
    }

    fetchResult()
  }, [tripId])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-3 text-gray-600">Loading your trip plan...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {error}
      </div>
    )
  }

  if (!htmlContent) {
    return (
      <div className="text-gray-600 text-center py-8">
        No content available
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-800">Your Trip Plan</h2>
        <button
          onClick={async () => {
            try {
              const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
              const response = await fetch(`${apiUrl}/api/trips/${tripId}/result/pdf`)
              
              if (!response.ok) {
                throw new Error('Failed to download PDF')
              }
              
              const blob = await response.blob()
              const url = URL.createObjectURL(blob)
              const a = document.createElement('a')
              a.href = url
              a.download = `trip_plan_${tripId}.pdf`
              a.click()
              URL.revokeObjectURL(url)
            } catch (err) {
              console.error('Error downloading PDF:', err)
              alert('Failed to download PDF. Please try again.')
            }
          }}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          📥 Download PDF
        </button>
      </div>

      {/* HTML Preview */}
      <div className="border border-gray-300 rounded-lg overflow-hidden">
        <iframe
          srcDoc={htmlContent}
          className="w-full h-[600px] border-0"
          title="Trip Plan Preview"
          sandbox="allow-same-origin"
        />
      </div>
    </div>
  )
}

