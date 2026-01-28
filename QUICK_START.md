# ⚡ Quick Start - Render Deployment

## 🎯 5-Minute Setup

### 1. Go to Render
👉 **https://render.com** → Sign up with GitHub

### 2. Create Web Service
- Click **"New +"** → **"Web Service"**
- Select repository: **`aidlink-app`**

### 3. Configure (Auto-detected from `render.yaml`)
- ✅ Build: `pip install -r requirements.txt`
- ✅ Start: `gunicorn AIDLINK.dynamic_app:app --bind 0.0.0.0:$PORT`

### 4. Add Environment Variables
Click **"Advanced"** → **"Environment Variables"**:

```
GOOGLE_PLACES_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

**Get API Keys:**
- Google Places: https://console.cloud.google.com/
- Gemini: https://makersuite.google.com/app/apikey

### 5. Deploy!
- Click **"Create Web Service"**
- Wait 5-10 minutes
- Your app: `https://aidlink.onrender.com`

---

## ✅ Test Your App

1. Visit: `https://aidlink.onrender.com`
2. Try a search: "food assistance" in "Sacramento, CA"
3. Test eligibility analysis

---

## 🔧 If Something Goes Wrong

**Build fails?** → Check logs in Render dashboard
**App won't start?** → Verify environment variables are set
**API calls fail?** → Check API keys are correct

**Full guide:** See `SETUP_INSTRUCTIONS.md`

---

## 📋 What You Need

- [x] GitHub repo (already done: `aidlink-app`)
- [ ] Render account (create now)
- [ ] Google Places API key (optional - app works without it)
- [ ] Gemini API key (optional - app works without it)

---

**That's it! Your app will be live in ~10 minutes! 🚀**

