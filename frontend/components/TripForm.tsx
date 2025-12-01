'use client'

import { useState } from 'react'

interface TripFormProps {
  clientId: string | null
  onTripCreated: (tripId: string, clientId: string) => void
}

export default function TripForm({ clientId, onTripCreated }: TripFormProps) {
  const [destination, setDestination] = useState('')
  const [duration, setDuration] = useState(7)
  const [budget, setBudget] = useState('moderate')
  const [travelStyle, setTravelStyle] = useState<string[]>([])
  const [specialRequirements, setSpecialRequirements] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const travelStyleOptions = [
    'Adventure',
    'Relaxation',
    'Cultural',
    'Food & Dining',
    'Nature & Outdoors',
    'Nightlife',
    'Family-Friendly',
    'Luxury',
    'Budget-Friendly',
  ]

  const toggleTravelStyle = (style: string) => {
    setTravelStyle(prev => {
      if (prev.includes(style)) {
        return prev.filter(s => s !== style)
      } else if (prev.length < 5) {
        return [...prev, style]
      }
      return prev
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    if (!destination.trim()) {
      setError('Please enter a destination')
      setLoading(false)
      return
    }

    if (travelStyle.length === 0) {
      setError('Please select at least one travel style')
      setLoading(false)
      return
    }

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/api/trips`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          destination: destination.trim(),
          duration,
          budget,
          travel_style: travelStyle,
          special_requirements: specialRequirements.trim() || undefined,
          client_id: clientId,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create trip')
      }

      const data = await response.json()
      onTripCreated(data.trip_id, data.client_id)
      
      // Reset form
      setDestination('')
      setDuration(7)
      setBudget('moderate')
      setTravelStyle([])
      setSpecialRequirements('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Destination */}
      <div>
        <label htmlFor="destination" className="block text-sm font-medium text-gray-700 mb-2">
          Destination *
        </label>
        <input
          type="text"
          id="destination"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          placeholder="e.g., Tokyo, Japan"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          required
          maxLength={100}
        />
      </div>

      {/* Duration */}
      <div>
        <label htmlFor="duration" className="block text-sm font-medium text-gray-700 mb-2">
          Duration: {duration} {duration === 1 ? 'day' : 'days'}
        </label>
        <input
          type="range"
          id="duration"
          min="1"
          max="30"
          value={duration}
          onChange={(e) => setDuration(parseInt(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>1 day</span>
          <span>30 days</span>
        </div>
      </div>

      {/* Budget */}
      <div>
        <label htmlFor="budget" className="block text-sm font-medium text-gray-700 mb-2">
          Budget
        </label>
        <select
          id="budget"
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="budget">Budget-Friendly</option>
          <option value="moderate">Moderate</option>
          <option value="luxury">Luxury</option>
        </select>
      </div>

      {/* Travel Style */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Travel Style * (select up to 5)
        </label>
        <div className="grid grid-cols-2 gap-2">
          {travelStyleOptions.map((style) => (
            <button
              key={style}
              type="button"
              onClick={() => toggleTravelStyle(style)}
              disabled={!travelStyle.includes(style) && travelStyle.length >= 5}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                travelStyle.includes(style)
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed'
              }`}
            >
              {style}
            </button>
          ))}
        </div>
        {travelStyle.length > 0 && (
          <p className="text-xs text-gray-500 mt-2">
            Selected: {travelStyle.join(', ')}
          </p>
        )}
      </div>

      {/* Special Requirements */}
      <div>
        <label htmlFor="specialRequirements" className="block text-sm font-medium text-gray-700 mb-2">
          Special Requirements (optional)
        </label>
        <textarea
          id="specialRequirements"
          value={specialRequirements}
          onChange={(e) => setSpecialRequirements(e.target.value)}
          placeholder="e.g., Wheelchair accessible, Vegetarian restaurants, etc."
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          maxLength={500}
        />
        <p className="text-xs text-gray-500 mt-1">
          {specialRequirements.length}/500 characters
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading || !clientId}
        className="w-full bg-primary-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Creating Trip Plan...' : 'Plan My Trip ✈️'}
      </button>
    </form>
  )
}

