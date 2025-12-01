import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Trip Planner - Plan Your Perfect Trip with AI',
  description: 'AI-powered trip planning with CrewAI. Get personalized day-by-day itineraries in seconds.',
  keywords: 'AI trip planner, travel itinerary, trip planning, AI travel agent, vacation planner',
  authors: [{ name: 'Zora Digital' }],
  openGraph: {
    title: 'AI Trip Planner - Plan Your Perfect Trip with AI',
    description: 'AI-powered trip planning with CrewAI. Get personalized day-by-day itineraries in seconds.',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

