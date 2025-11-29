# 🔒 Security Features

This document describes the security features implemented in the AI Trip Planner to protect against abuse, attacks, and unexpected costs.

## 🛡️ Implemented Security Features

### 1. Rate Limiting

Prevents abuse by limiting the number of trip plans per session.

**Default Limits:**
- **5 trips per hour** - Prevents rapid-fire abuse
- **20 trips per day** - Reasonable daily usage cap

**How it works:**
- Tracks trips per session using Streamlit session state
- Automatically resets hourly and daily counters
- Shows clear error messages when limits are reached
- Displays usage statistics in the sidebar

**Configuration:**
Edit `MAX_TRIPS_PER_HOUR` and `MAX_TRIPS_PER_DAY` in `app.py` or `security_config.py`

---

### 2. Input Validation

Protects against malicious inputs and prompt injection attacks.

**Validations:**
- ✅ **Length limits:**
  - Destination: 100 characters max
  - Duration: 30 days max
  - Special requirements: 500 characters max

- ✅ **Pattern detection:**
  - SQL injection attempts (SELECT, DROP, INSERT, etc.)
  - XSS attacks (`<script>`, `javascript:`, etc.)
  - Path traversal (`../`, `..\`)
  - Code execution attempts (`exec`, `eval`)

**How it works:**
- Validates all user inputs before processing
- Uses regex patterns to detect suspicious content
- Rejects requests with clear error messages
- Sanitizes inputs to prevent prompt injection

**Configuration:**
Edit validation limits and patterns in `security_config.py`

---

### 3. Cost Cap

Protects your budget by limiting daily API spending.

**Default Settings:**
- **Daily cap:** $10.00 USD
- **Estimated cost per trip:** $0.03 (with gpt-4o-mini)

**How it works:**
- Tracks estimated costs per trip
- Accumulates daily spending
- Blocks new requests when cap is reached
- Resets automatically at midnight
- Shows remaining budget in sidebar

**Cost Estimates by Model:**
| Model | Cost per Trip |
|-------|---------------|
| gpt-4o-mini | $0.01-0.03 |
| gpt-4o | $0.08-0.15 |
| gpt-4-turbo | $0.30-0.50 |
| gpt-4 | $0.90-1.50 |

**Configuration:**
Edit `DAILY_COST_CAP_USD` and `ESTIMATED_COST_PER_TRIP` in `security_config.py`

---

## 📊 Usage Statistics Dashboard

The sidebar displays real-time usage statistics:

```
📊 Usage Stats
┌─────────────────┬─────────────────┐
│ Trips (Hour)    │ Trips (Day)     │
│ 2/5             │ 8/20            │
├─────────────────┼─────────────────┤
│ Cost Today      │ Budget Left     │
│ $0.240          │ $9.76           │
└─────────────────┴─────────────────┘
```

**Warnings:**
- ⚠️ Yellow warning at 80% of hourly limit
- ⚠️ Yellow warning at 80% of daily cost cap
- 🚫 Red error when limits are exceeded

---

## 🔐 Security Best Practices

### For Deployment

1. **Environment Variables**
   - ✅ Never commit `.env` file
   - ✅ Use Streamlit secrets for cloud deployment
   - ✅ Rotate API keys if exposed

2. **API Keys**
   - Store in `.env` file locally
   - Use Streamlit Cloud secrets for production
   - Set up billing alerts in OpenAI dashboard

3. **Monitoring**
   - Check usage statistics regularly
   - Monitor OpenAI usage dashboard
   - Set up cost alerts

### Recommended Settings by Use Case

#### Personal Use (Default)
```python
MAX_TRIPS_PER_HOUR = 5
MAX_TRIPS_PER_DAY = 20
DAILY_COST_CAP_USD = 10.0
```

#### Small Team (5-10 users)
```python
MAX_TRIPS_PER_HOUR = 10
MAX_TRIPS_PER_DAY = 50
DAILY_COST_CAP_USD = 25.0
```

#### Public Beta
```python
MAX_TRIPS_PER_HOUR = 3
MAX_TRIPS_PER_DAY = 10
DAILY_COST_CAP_USD = 5.0
```

#### Production
- Implement user authentication
- Use database for tracking
- Per-user rate limiting
- Payment/subscription system

---

## 🚨 What's NOT Protected (Yet)

These features require additional infrastructure:

1. **User Authentication** - Currently session-based only
2. **IP-based Rate Limiting** - Would require server-side tracking
3. **Database Persistence** - Rate limits reset on app restart
4. **DDoS Protection** - Rely on Streamlit Cloud's infrastructure
5. **Advanced Monitoring** - No logging or analytics yet

---

## 🛠️ Customization

### Adjusting Rate Limits

Edit the configuration at the top of `app.py`:

```python
# Configuration
MAX_TRIPS_PER_HOUR = 5      # Adjust as needed
MAX_TRIPS_PER_DAY = 20       # Adjust as needed
DAILY_COST_CAP_USD = 10.0    # Adjust based on budget
```

### Adding Custom Validation

Add patterns to the `suspicious_patterns` list in `validate_input()`:

```python
suspicious_patterns = [
    r'your_custom_pattern',
    # ... existing patterns
]
```

### Changing Cost Estimates

Update based on your actual usage:

```python
ESTIMATED_COST_PER_TRIP = 0.03  # Adjust based on model and trip complexity
```

---

## 📈 Monitoring Your Costs

### OpenAI Dashboard
1. Go to https://platform.openai.com/usage
2. Set up billing alerts
3. Monitor daily/monthly usage

### In-App Monitoring
- Check "Usage Stats" in sidebar
- Monitor "Cost Today" metric
- Watch for warning messages

---

## 🐛 Troubleshooting

### "Rate limit exceeded" error
- **Cause:** Too many trips in short time
- **Solution:** Wait until next hour/day or adjust limits

### "Daily cost cap reached" error
- **Cause:** Reached spending limit
- **Solution:** Wait until tomorrow or increase `DAILY_COST_CAP_USD`

### "Invalid characters detected" error
- **Cause:** Input contains suspicious patterns
- **Solution:** Rephrase input, remove special characters

### Rate limits reset unexpectedly
- **Cause:** App restarted (session state cleared)
- **Solution:** Normal behavior - for persistent tracking, use a database

---

## 🔄 Future Enhancements

Potential improvements for production:

1. **Database Integration**
   - Persistent rate limiting across restarts
   - Historical usage tracking
   - User management

2. **Advanced Authentication**
   - OAuth integration
   - API key management
   - User tiers/subscriptions

3. **Enhanced Monitoring**
   - Real-time cost tracking
   - Usage analytics
   - Error logging (Sentry, etc.)

4. **IP-based Rate Limiting**
   - Prevent session-hopping abuse
   - Requires server-side implementation

---

## 📞 Support

For security concerns or questions:
1. Review this documentation
2. Check `security_config.py` for settings
3. Consult OpenAI's security best practices
4. Monitor your OpenAI usage dashboard

---

## ⚖️ License & Compliance

- Ensure compliance with OpenAI's usage policies
- Review data privacy requirements for your region
- Implement appropriate user consent mechanisms
- Follow GDPR/CCPA guidelines if applicable

