"""
Security and rate limiting configuration for the Trip Planner API
"""

# Rate limiting
MAX_TRIPS_PER_HOUR = 10
MAX_TRIPS_PER_DAY = 50

# Cost limits (in USD)
DAILY_COST_CAP_USD = 1000.0  # Maximum daily cost cap
ESTIMATED_COST_PER_TRIP = 5.0  # Estimated cost per trip in USD

# Input validation limits
MAX_DESTINATION_LENGTH = 200
MAX_DURATION_DAYS = 365
MAX_SPECIAL_REQUIREMENTS_LENGTH = 1000

# Suspicious patterns for security
SUSPICIOUS_PATTERNS = [
    r"<script",
    r"javascript:",
    r"onerror=",
    r"onload=",
    r"eval\(",
    r"exec\(",
]

