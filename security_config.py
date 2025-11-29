"""
Security Configuration for AI Trip Planner

Adjust these settings based on your deployment needs:
- For personal use: Keep defaults or increase limits
- For public deployment: Consider stricter limits
- For production: Add user authentication and database tracking
"""

# ============================================================================
# RATE LIMITING
# ============================================================================

# Maximum number of trip plans per hour per session
MAX_TRIPS_PER_HOUR = 5

# Maximum number of trip plans per day per session
MAX_TRIPS_PER_DAY = 20

# ============================================================================
# COST MANAGEMENT
# ============================================================================

# Maximum daily spending in USD (protects your OpenAI budget)
DAILY_COST_CAP_USD = 10.0

# Estimated cost per trip in USD (adjust based on your actual usage)
# With gpt-4o-mini: ~$0.01-0.03 per trip
# With gpt-4o: ~$0.08-0.15 per trip
ESTIMATED_COST_PER_TRIP = 0.03

# ============================================================================
# INPUT VALIDATION
# ============================================================================

# Maximum length for destination input (prevents abuse)
MAX_DESTINATION_LENGTH = 100

# Maximum trip duration in days
MAX_DURATION_DAYS = 30

# Maximum length for special requirements
MAX_SPECIAL_REQUIREMENTS_LENGTH = 500

# ============================================================================
# SECURITY PATTERNS
# ============================================================================

# Patterns to detect malicious input
# These are basic protections - consider adding more for production
SUSPICIOUS_PATTERNS = [
    r'(\bSELECT\b|\bDROP\b|\bINSERT\b|\bUPDATE\b|\bDELETE\b)',  # SQL injection
    r'(<script|javascript:|onerror=)',  # XSS attempts
    r'(\.\.\/|\.\.\\)',  # Path traversal
    r'(\bexec\b|\beval\b)',  # Code execution attempts
]

# ============================================================================
# MONITORING & ALERTS
# ============================================================================

# Percentage thresholds for warnings
HOURLY_LIMIT_WARNING_THRESHOLD = 0.8  # Warn at 80% of hourly limit
DAILY_COST_WARNING_THRESHOLD = 0.8    # Warn at 80% of daily cost cap

# ============================================================================
# NOTES
# ============================================================================

"""
Recommended Settings by Deployment Type:

PERSONAL USE (Default):
- MAX_TRIPS_PER_HOUR: 5
- MAX_TRIPS_PER_DAY: 20
- DAILY_COST_CAP_USD: 10.0

SMALL TEAM (5-10 users):
- MAX_TRIPS_PER_HOUR: 10
- MAX_TRIPS_PER_DAY: 50
- DAILY_COST_CAP_USD: 25.0

PUBLIC BETA (Limited access):
- MAX_TRIPS_PER_HOUR: 3
- MAX_TRIPS_PER_DAY: 10
- DAILY_COST_CAP_USD: 5.0

PRODUCTION (With authentication):
- Implement per-user rate limiting
- Use database for tracking
- Add payment/subscription system
- Increase limits based on user tier
"""

