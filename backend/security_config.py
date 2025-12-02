"""
Security and rate limiting configuration for the Trip Planner API
"""

# Rate limiting
MAX_TRIPS_PER_HOUR = 5
MAX_TRIPS_PER_DAY = 5

# Cost limits (in USD)
DAILY_COST_CAP_USD = 2.50  # Maximum daily cost cap
ESTIMATED_COST_PER_TRIP = 0.50  # Estimated cost per trip in USD

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

