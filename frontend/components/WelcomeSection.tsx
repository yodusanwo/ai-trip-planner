'use client'

export default function WelcomeSection() {
  return (
    <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
      {/* Welcome Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          ✨ Welcome!
        </h2>
        <p className="text-lg text-gray-700">
          Our AI agents will help you plan the perfect trip:
        </p>
      </div>

      {/* AI Agents Section */}
      <div className="mb-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Trip Researcher */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border-2 border-blue-200">
            <div className="flex items-center mb-3">
              <span className="text-3xl mr-3">🔍</span>
              <h3 className="text-xl font-semibold text-gray-800">Trip Researcher</h3>
            </div>
            <p className="text-gray-700 text-sm">
              Finds the best attractions, restaurants, and activities
            </p>
          </div>

          {/* Trip Reviewer */}
          <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-6 border-2 border-yellow-200">
            <div className="flex items-center mb-3">
              <span className="text-3xl mr-3">⭐</span>
              <h3 className="text-xl font-semibold text-gray-800">Trip Reviewer</h3>
            </div>
            <p className="text-gray-700 text-sm">
              Analyzes and prioritizes recommendations
            </p>
          </div>

          {/* Trip Planner */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border-2 border-purple-200">
            <div className="flex items-center mb-3">
              <span className="text-3xl mr-3">📋</span>
              <h3 className="text-xl font-semibold text-gray-800">Trip Planner</h3>
            </div>
            <p className="text-gray-700 text-sm">
              Creates a beautiful day-by-day itinerary
            </p>
          </div>
        </div>
      </div>

      {/* Divider */}
      <div className="border-t border-gray-200 my-8"></div>

      {/* How to Use Section */}
      <div>
        <h3 className="text-2xl font-semibold text-gray-800 mb-6">
          How to use:
        </h3>
        <div className="space-y-4">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
              1
            </div>
            <p className="text-gray-700 pt-1">
              Enter your destination and trip duration
            </p>
          </div>
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
              2
            </div>
            <p className="text-gray-700 pt-1">
              Select your budget level and travel style
            </p>
          </div>
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
              3
            </div>
            <p className="text-gray-700 pt-1">
              Add any special requirements
            </p>
          </div>
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
              4
            </div>
            <p className="text-gray-700 pt-1">
              Click <span className="font-semibold text-blue-600">"Plan My Trip"</span> and let our AI agents work their magic!
            </p>
          </div>
        </div>
      </div>

      {/* Estimated Time */}
      <div className="mt-8 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-6 border-2 border-green-200">
        <div className="flex items-center justify-center space-x-2">
          <span className="text-2xl">⚡</span>
          <p className="text-gray-800">
            Your personalized trip plan will be ready in{' '}
            <span className="font-bold text-green-700">45 seconds to 2.5 minutes</span>{' '}
            depending on trip length!
          </p>
        </div>
      </div>
    </div>
  )
}

