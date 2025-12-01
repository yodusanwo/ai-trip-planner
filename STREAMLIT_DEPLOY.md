# 🚀 Deploy to Streamlit Cloud

Quick guide to deploy your AI Trip Planner to Streamlit Cloud.

## ✅ Prerequisites

- ✅ GitHub account
- ✅ Code pushed to GitHub (Done!)
- ✅ OpenAI API key
- ✅ Serper API key

---

## 📋 Step-by-Step Deployment

### Step 1: Go to Streamlit Cloud

Visit: **https://share.streamlit.io**

### Step 2: Sign In

- Click "Sign in"
- Choose "Continue with GitHub"
- Authorize Streamlit

### Step 3: Create New App

1. Click "New app" button
2. Fill in the form:

```
Repository: Zora-Digital/trip_planner
Branch: main
Main file path: app.py
App URL: your-custom-name (e.g., ai-trip-planner)
```

### Step 4: Advanced Settings - Add Secrets

Click "Advanced settings" → "Secrets"

Add your API keys:

```toml
OPENAI_API_KEY = "sk-your-openai-key-here"
SERPER_API_KEY = "your-serper-key-here"
MODEL = "gpt-4o-mini"
```

**Important:** 
- Don't include quotes around the values in Streamlit secrets
- Make sure there are no extra spaces
- Each key should be on its own line

### Step 5: Deploy!

Click "Deploy" button

---

## ⏱️ Deployment Process

```
1. Building... (1-2 minutes)
   └─ Installing dependencies
   └─ Setting up environment

2. Deploying... (30 seconds)
   └─ Starting app
   └─ Running health checks

3. Live! 🎉
   └─ Your app is now public
```

---

## 🌐 Your App URL

After deployment, your app will be available at:

```
https://your-custom-name.streamlit.app
```

Or Streamlit will assign:

```
https://zora-digital-trip-planner-app-xyz123.streamlit.app
```

---

## 🔧 Post-Deployment Configuration

### Update Security Settings (Optional)

For public deployment, you may want stricter limits:

1. Go to your GitHub repo
2. Edit `app.py`
3. Update these values:

```python
# For public deployment
MAX_TRIPS_PER_HOUR = 3      # Stricter
MAX_TRIPS_PER_DAY = 10       # Stricter  
DAILY_COST_CAP_USD = 5.0     # Lower cap
```

4. Commit and push
5. Streamlit will auto-redeploy

---

## 📊 Monitor Your App

### Streamlit Cloud Dashboard

Access at: https://share.streamlit.io

**Features:**
- View logs
- Monitor usage
- Restart app
- Update secrets
- Manage settings

### OpenAI Usage

Monitor costs at: https://platform.openai.com/usage

**Set up:**
- Billing alerts
- Usage limits
- Monthly budgets

---

## 🔒 Security Checklist

Before going public, verify:

- ✅ API keys are in Streamlit secrets (not in code)
- ✅ `.env` file is in `.gitignore`
- ✅ Rate limiting is enabled
- ✅ Input validation is active
- ✅ Cost cap is set appropriately
- ✅ Usage dashboard is visible

---

## 🐛 Troubleshooting

### App Won't Start

**Check logs:**
1. Go to Streamlit Cloud dashboard
2. Click on your app
3. View "Logs" tab

**Common issues:**
- Missing secrets → Add in Advanced Settings
- Wrong file path → Should be `app.py`
- Dependency errors → Check `requirements.txt`

### API Errors

**"Invalid API key":**
- Verify keys in Streamlit secrets
- Check for extra spaces
- Ensure no quotes around values

**"Rate limit exceeded":**
- Normal! Security feature working
- Adjust limits in `app.py` if needed

### Slow Performance

**First load is slow:**
- Normal for cold starts
- Subsequent loads are faster

**Execution is slow:**
- Check OpenAI API status
- Verify you're using `gpt-4o-mini`
- Review `max_iter` settings

---

## 🔄 Update Your App

### Automatic Deployment

Streamlit auto-deploys when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push

# Streamlit automatically redeploys!
```

### Manual Reboot

From Streamlit Cloud dashboard:
1. Click on your app
2. Click "⋮" menu
3. Select "Reboot app"

---

## 📈 Scaling Options

### Free Tier Limits

- ✅ Unlimited public apps
- ✅ 1GB RAM per app
- ✅ Community support

### If You Need More

**Streamlit Community Cloud:**
- More resources
- Custom domains
- Priority support
- Team collaboration

Visit: https://streamlit.io/cloud

---

## 🎨 Custom Domain (Optional)

### Add Custom Domain

1. Go to app settings
2. Click "Custom domain"
3. Add your domain (e.g., `trip.zoradigital.com`)
4. Follow DNS configuration instructions

**Requirements:**
- Own a domain
- Access to DNS settings
- Streamlit paid plan

---

## 📱 Share Your App

### Social Media

Your preview images will automatically show when shared on:
- Facebook
- Twitter/X
- LinkedIn
- Slack
- Discord

### Embed

Add to your website:

```html
<iframe 
  src="https://your-app.streamlit.app?embed=true"
  width="100%" 
  height="800px"
  frameborder="0">
</iframe>
```

---

## 🎉 You're Live!

Your AI Trip Planner is now:

✅ **Deployed** to Streamlit Cloud  
✅ **Secured** with rate limiting  
✅ **Branded** with Zora Digital  
✅ **Optimized** for performance  
✅ **Ready** for users!

---

## 📞 Support

**Streamlit:**
- Docs: https://docs.streamlit.io
- Forum: https://discuss.streamlit.io
- Status: https://status.streamlit.io

**Your App:**
- GitHub: https://github.com/Zora-Digital/trip_planner
- Issues: https://github.com/Zora-Digital/trip_planner/issues

---

## 🚀 Next Steps

1. ✅ Deploy to Streamlit Cloud
2. Test all features
3. Share on social media
4. Monitor usage and costs
5. Gather user feedback
6. Iterate and improve!

**Happy deploying! 🎊**

