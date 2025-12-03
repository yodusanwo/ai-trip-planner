'use client'

import { useState, useEffect, useCallback } from 'react'

export interface TripDetails {
  destination: string
  duration: number
  budget: string
  travelStyle: string[]
  specialRequirements?: string
}

interface TripFormProps {
  clientId: string | null
  onTripCreated: (tripId: string, clientId: string, tripDetails: TripDetails) => void
}

interface SpellCheckResult {
  has_errors: boolean
  misspelled_words: string[]
  suggestions: { [word: string]: string[] }
  original_text: string
  error?: string
}

export default function TripForm({ clientId, onTripCreated }: TripFormProps) {
  const [destination, setDestination] = useState('')
  const [duration, setDuration] = useState(7)
  const [budget, setBudget] = useState('moderate')
  const [travelStyle, setTravelStyle] = useState<string[]>([])
  const [specialRequirements, setSpecialRequirements] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [destinationSpellCheck, setDestinationSpellCheck] = useState<SpellCheckResult | null>(null)
  const [requirementsSpellCheck, setRequirementsSpellCheck] = useState<SpellCheckResult | null>(null)
  const [checkingSpell, setCheckingSpell] = useState(false)

  const travelStyleOptions = [
    'Adventure',
    'Relaxation',
    'Cultural',
    'Food & Dining',
    'Nature & Outdoors',
    'Nightlife',
    'Family-Friendly',
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

  // Debounced spell check function
  const spellCheckText = useCallback(async (text: string, type: 'destination' | 'requirements') => {
    if (!text.trim() || text.trim().length < 3) {
      if (type === 'destination') {
        setDestinationSpellCheck(null)
      } else {
        setRequirementsSpellCheck(null)
      }
      return
    }

    setCheckingSpell(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      console.log(`[Spell Check] Checking ${type}: "${text}"`)
      
      const response = await fetch(`${apiUrl}/api/spell-check`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      })

      if (response.ok) {
        const result: SpellCheckResult = await response.json()
        console.log(`[Spell Check] Result for ${type}:`, result)
        
        if (type === 'destination') {
          setDestinationSpellCheck(result)
        } else {
          setRequirementsSpellCheck(result)
        }
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
        console.error(`[Spell Check] API error for ${type}:`, errorData)
      }
    } catch (err) {
      console.error(`[Spell Check] Error checking ${type}:`, err)
    } finally {
      setCheckingSpell(false)
    }
  }, [])

  // Debounce spell check for destination
  useEffect(() => {
    const timer = setTimeout(() => {
      if (destination.trim() && destination.trim().length >= 3) {
        spellCheckText(destination, 'destination')
      } else {
        setDestinationSpellCheck(null)
      }
    }, 500) // Wait 500ms after user stops typing

    return () => clearTimeout(timer)
  }, [destination, spellCheckText])

  // Debounce spell check for special requirements
  useEffect(() => {
    const timer = setTimeout(() => {
      if (specialRequirements.trim() && specialRequirements.trim().length >= 3) {
        spellCheckText(specialRequirements, 'requirements')
      } else {
        setRequirementsSpellCheck(null)
      }
    }, 500) // Wait 500ms after user stops typing

    return () => clearTimeout(timer)
  }, [specialRequirements, spellCheckText])

  // Apply spell check suggestion
  const applySuggestion = (originalWord: string, suggestion: string, type: 'destination' | 'requirements') => {
    const currentText = type === 'destination' ? destination : specialRequirements
    const regex = new RegExp(`\\b${originalWord}\\b`, 'gi')
    const newText = currentText.replace(regex, suggestion)
    
    if (type === 'destination') {
      setDestination(newText)
      setDestinationSpellCheck(null)
    } else {
      setSpecialRequirements(newText)
      setRequirementsSpellCheck(null)
    }
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
      
      // Pass trip details along with trip ID
      const tripDetails: TripDetails = {
        destination: destination.trim(),
        duration,
        budget,
        travelStyle,
        specialRequirements: specialRequirements.trim() || undefined,
      }
      
      onTripCreated(data.trip_id, data.client_id, tripDetails)
      
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
          spellCheck="true"
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
            destinationSpellCheck?.has_errors ? 'border-yellow-400' : 'border-gray-300'
          }`}
          required
          maxLength={100}
        />
        {checkingSpell && destination.trim().length >= 3 && (
          <div className="mt-2 text-xs text-gray-500">
            Checking spelling...
          </div>
        )}
        {destinationSpellCheck?.error && (
          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-xs text-red-700">
              ⚠️ Spell checker unavailable: {destinationSpellCheck.error}
            </p>
          </div>
        )}
        {destinationSpellCheck?.has_errors && !destinationSpellCheck?.error && (
          <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm font-medium text-yellow-800 mb-2">
              ⚠️ Possible spelling issues detected:
            </p>
            <p className="text-xs text-yellow-700 mb-2 italic">
              Note: Place names may not be recognized by the spell checker.
            </p>
            <div className="space-y-1">
              {destinationSpellCheck.misspelled_words.map((word) => {
                // Try to find suggestions with case-insensitive matching
                const suggestionKey = Object.keys(destinationSpellCheck.suggestions).find(
                  key => key.toLowerCase() === word.toLowerCase()
                ) || word
                const suggestions = destinationSpellCheck.suggestions[suggestionKey] || []
                
                return (
                  <div key={word} className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm text-yellow-800 font-medium">"{word}"</span>
                    {suggestions.length > 0 && (
                      <>
                        <span className="text-xs text-yellow-600">→</span>
                        {suggestions.map((suggestion) => (
                          <button
                            key={suggestion}
                            type="button"
                            onClick={() => applySuggestion(word, suggestion, 'destination')}
                            className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded hover:bg-yellow-200 transition-colors"
                          >
                            {suggestion}
                          </button>
                        ))}
                      </>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}
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
          spellCheck="true"
          className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
            requirementsSpellCheck?.has_errors ? 'border-yellow-400' : 'border-gray-300'
          }`}
          maxLength={500}
        />
        <p className="text-xs text-gray-500 mt-1">
          {specialRequirements.length}/500 characters
        </p>
        {checkingSpell && specialRequirements.trim().length >= 3 && (
          <div className="mt-2 text-xs text-gray-500">
            Checking spelling...
          </div>
        )}
        {requirementsSpellCheck?.error && (
          <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-xs text-red-700">
              ⚠️ Spell checker unavailable: {requirementsSpellCheck.error}
            </p>
          </div>
        )}
        {requirementsSpellCheck?.has_errors && !requirementsSpellCheck?.error && (
          <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm font-medium text-yellow-800 mb-2">
              ⚠️ Possible spelling issues detected:
            </p>
            <div className="space-y-1">
              {requirementsSpellCheck.misspelled_words.map((word) => {
                // Try to find suggestions with case-insensitive matching
                const suggestionKey = Object.keys(requirementsSpellCheck.suggestions).find(
                  key => key.toLowerCase() === word.toLowerCase()
                ) || word
                const suggestions = requirementsSpellCheck.suggestions[suggestionKey] || []
                
                return (
                  <div key={word} className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm text-yellow-800 font-medium">"{word}"</span>
                    {suggestions.length > 0 && (
                      <>
                        <span className="text-xs text-yellow-600">→</span>
                        {suggestions.map((suggestion) => (
                          <button
                            key={suggestion}
                            type="button"
                            onClick={() => applySuggestion(word, suggestion, 'requirements')}
                            className="text-xs px-2 py-1 bg-yellow-100 text-yellow-800 rounded hover:bg-yellow-200 transition-colors"
                          >
                            {suggestion}
                          </button>
                        ))}
                      </>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        )}
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

