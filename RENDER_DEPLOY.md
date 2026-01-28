# Quick Render Deployment Guide

Your app is ready to deploy to Render! Follow these simple steps:

## 🚀 Deploy in 5 Minutes

### Step 1: Push Code to GitHub
Your code is already on GitHub at:
- **New repo**: https://github.com/Lasp10/aidlink-app
- **Old repo**: https://github.com/Lasp10/Aidlink

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with your GitHub account (recommended)

### Step 3: Create New Web Service
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub account if not already connected
3. Select repository: **`aidlink-app`** (or `Aidlink`)

### Step 4: Configure Service
Render will auto-detect your `render.yaml` file, but you can also configure manually:

**Manual Configuration:**
- **Name**: `aidlink` (or your choice)
- **Environment**: `Python 3`
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: Leave empty (or `AIDLINK/` if you prefer)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn AIDLINK.dynamic_app:app --bind 0.0.0.0:$PORT`

### Step 5: Set Environment Variables
Click **"Advanced"** → **"Environment Variables"** and add:

```
GOOGLE_PLACES_API_KEY=your_actual_google_places_key_here
GEMINI_API_KEY=your_actual_gemini_key_here
PORT=10000
DEBUG=False
FLASK_ENV=production
```

**Important:** Replace `your_actual_google_places_key_here` and `your_actual_gemini_key_here` with your real API keys!

### Step 6: Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for build to complete
3. Your app will be live at: `https://aidlink.onrender.com` (or your chosen name)

### Step 7: Test Your App
Visit your Render URL and test:
- ✅ Homepage loads
- ✅ Search functionality works
- ✅ API endpoints respond

---

## 🌐 Add Custom Domain (Optional)

### In Render Dashboard:
1. Go to your service → **"Settings"** → **"Custom Domains"**
2. Click **"Add Custom Domain"**
3. Enter your domain (e.g., `aidlink.com` or `www.aidlink.com`)
4. Render will show DNS records to add

### At Your Domain Registrar:
Add the DNS records Render provides:
- **CNAME** for www subdomain
- **A Record** for root domain

SSL certificate will be automatically provisioned (takes 24-48 hours).

---

## 📋 Quick Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service created
- [ ] Environment variables set (API keys)
- [ ] Deployment successful
- [ ] App tested and working
- [ ] Custom domain added (optional)

---

## 🔧 Troubleshooting

### Build Fails
- Check build logs in Render dashboard
- Verify `requirements.txt` is correct
- Ensure Python version is compatible (3.11+)

### App Doesn't Start
- Check start command is correct
- Verify `PORT` environment variable is set
- Check application logs

### API Calls Fail
- Verify API keys are set correctly
- Check CORS settings (should work by default)
- Review application logs for errors

### 502 Bad Gateway
- App might be starting up (wait 1-2 minutes)
- Check if app is listening on correct port
- Review logs for startup errors

---

## 💡 Pro Tips

1. **Free Tier Limits:**
   - Services spin down after 15 minutes of inactivity
   - First request after spin-down takes ~30 seconds
   - Upgrade to paid plan for always-on service

2. **Environment Variables:**
   - Never commit API keys to GitHub
   - Use Render's environment variable settings
   - Keep `.gitignore` to protect secrets

3. **Monitoring:**
   - Check logs regularly in Render dashboard
   - Set up alerts for errors
   - Monitor API usage

4. **Updates:**
   - Push to GitHub → Render auto-deploys
   - Or manually trigger deployment in dashboard

---

## 🎉 You're Done!

Your AidLink app is now live on Render! 

**Next Steps:**
- Share your app URL
- Add custom domain
- Monitor usage and logs
- Set up alerts

**Need Help?**
- Render Docs: https://render.com/docs
- Render Support: Available in dashboard

