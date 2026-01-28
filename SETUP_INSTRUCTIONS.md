# 🚀 Render Deployment - Step-by-Step Setup Guide

Follow these instructions to deploy your AidLink app to Render.

---

## 📋 Prerequisites Checklist

Before you start, make sure you have:
- [x] ✅ Code pushed to GitHub (already done: `aidlink-app`)
- [ ] ⚠️ Google Places API Key (get from [Google Cloud Console](https://console.cloud.google.com/))
- [ ] ⚠️ Gemini API Key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

**Don't have API keys yet?** That's okay - you can deploy first and add them later. The app will work with fallback data.

---

## 🎯 Step 1: Create Render Account

1. **Go to Render:** Open [https://render.com](https://render.com) in your browser
2. **Sign Up:** Click **"Get Started for Free"** (top right)
3. **Choose Sign Up Method:**
   - **Recommended:** Click **"Sign up with GitHub"** 
   - This automatically connects your GitHub account
   - Authorize Render to access your repositories
4. **Complete Profile:** Fill in your email and password if needed

**✅ You're now logged into Render!**

---

## 🎯 Step 2: Create New Web Service

1. **In Render Dashboard:** Click the **"New +"** button (top right)
2. **Select Service Type:** Click **"Web Service"**
3. **Connect Repository:**
   - If you signed up with GitHub, your repos should appear automatically
   - If not, click **"Connect account"** and authorize GitHub
   - **Select repository:** `aidlink-app` (or `Lasp10/aidlink-app`)

**✅ Repository connected!**

---

## 🎯 Step 3: Configure Your Service

Render will auto-detect your `render.yaml` file, but here's what to verify:

### Basic Settings:
- **Name:** `aidlink` (or your preferred name)
- **Region:** Choose closest to you (e.g., `Oregon (US West)`)
- **Branch:** `main` (should be auto-selected)
- **Root Directory:** Leave **empty** (or set to `/`)

### Build & Start Commands:
These should auto-populate from `render.yaml`, but verify:

- **Environment:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn AIDLINK.dynamic_app:app --bind 0.0.0.0:$PORT`

**✅ Configuration looks good!**

---

## 🎯 Step 4: Set Environment Variables

**This is important!** Click **"Advanced"** at the bottom, then **"Environment Variables"**.

### Add These Variables:

Click **"Add Environment Variable"** for each:

1. **GOOGLE_PLACES_API_KEY**
   - **Key:** `GOOGLE_PLACES_API_KEY`
   - **Value:** Your actual Google Places API key
   - **Note:** If you don't have one yet, you can add it later. The app will use fallback data.

2. **GEMINI_API_KEY**
   - **Key:** `GEMINI_API_KEY`
   - **Value:** Your actual Gemini API key
   - **Note:** If you don't have one yet, you can add it later. The app will use fallback analysis.

3. **PORT** (Optional - Render sets this automatically)
   - **Key:** `PORT`
   - **Value:** `10000`
   - **Note:** Render sets this automatically, but you can specify it.

4. **DEBUG** (Optional)
   - **Key:** `DEBUG`
   - **Value:** `False`
   - **Note:** Keeps debug mode off in production.

5. **FLASK_ENV** (Optional)
   - **Key:** `FLASK_ENV`
   - **Value:** `production`

### How to Get API Keys:

**Google Places API Key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable "Places API"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the key

**Gemini API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

**⚠️ Important:** Keep your API keys secret! Never commit them to GitHub.

**✅ Environment variables added!**

---

## 🎯 Step 5: Deploy!

1. **Review Settings:** Double-check everything looks correct
2. **Click:** **"Create Web Service"** (bottom of page)
3. **Wait for Build:** 
   - Render will start building your app
   - This takes 5-10 minutes
   - You'll see build logs in real-time
4. **Watch the Logs:**
   - Build process: Installing dependencies
   - Starting app: Should see "Listening on port..."
   - **Success:** You'll see "Your service is live at..."

**✅ Deployment in progress!**

---

## 🎯 Step 6: Get Your App URL

Once deployment completes:

1. **Your app URL will be:** `https://aidlink.onrender.com` (or your chosen name)
2. **Test it:** Click the URL or copy it to your browser
3. **Verify it works:**
   - Homepage loads ✅
   - Search works ✅
   - API endpoints respond ✅

**✅ Your app is live!**

---

## 🎯 Step 7: Test Your App

1. **Visit your app URL** (e.g., `https://aidlink.onrender.com`)
2. **Test Search:**
   - Enter a query: "food assistance"
   - Enter location: "Sacramento, CA"
   - Click "Search"
   - Should see results

3. **Test Eligibility Analysis:**
   - Click "Analyze Eligibility" on a resource
   - Enter a situation description
   - Should see AI analysis

**✅ Everything working!**

---

## 🌐 Optional: Add Custom Domain

Want to use your own domain (e.g., `aidlink.com`)?

### In Render Dashboard:
1. Go to your service → **"Settings"** tab
2. Scroll to **"Custom Domains"**
3. Click **"Add Custom Domain"**
4. Enter your domain: `aidlink.com` or `www.aidlink.com`
5. Render will show DNS records to add

### At Your Domain Registrar:
1. Go to your domain provider (Namecheap, GoDaddy, etc.)
2. Open DNS settings
3. Add the DNS records Render provides:
   - **CNAME** for `www` subdomain
   - **A Record** for root domain
4. Save changes

### Wait for SSL:
- DNS propagation: 24-48 hours
- SSL certificate: Auto-provisioned by Render
- Your app will be at: `https://aidlink.com`

**✅ Custom domain configured!**

---

## 🔧 Troubleshooting

### Build Fails
**Problem:** Build command fails
**Solution:**
- Check build logs in Render dashboard
- Verify `requirements.txt` exists in root
- Ensure Python version is 3.11+

### App Won't Start
**Problem:** Service shows "Failed" status
**Solution:**
- Check application logs
- Verify start command is correct
- Ensure `PORT` environment variable is set
- Check if `index.html` exists in root directory

### API Calls Fail
**Problem:** Search/eligibility features don't work
**Solution:**
- Verify API keys are set correctly
- Check application logs for errors
- Ensure CORS is enabled (should be by default)
- Test API endpoints directly: `https://your-app.onrender.com/api/status`

### 502 Bad Gateway
**Problem:** App shows error page
**Solution:**
- App might be spinning up (free tier spins down after 15 min inactivity)
- Wait 30 seconds and refresh
- Check logs for startup errors
- Verify gunicorn is installed in requirements.txt

### Slow First Load
**Problem:** First request takes 30+ seconds
**Solution:**
- This is normal on free tier (service spins down after inactivity)
- First request "wakes up" the service
- Subsequent requests are fast
- Upgrade to paid plan for always-on service

---

## 📊 Monitoring Your App

### View Logs:
1. Go to your service in Render dashboard
2. Click **"Logs"** tab
3. See real-time application logs
4. Filter by errors, warnings, etc.

### Check Status:
- **Live:** App is running
- **Deploying:** Build in progress
- **Failed:** Check logs for errors

### Update Your App:
1. Make changes to your code
2. Push to GitHub: `git push origin main`
3. Render **automatically deploys** the update!
4. Wait 5-10 minutes for new deployment

---

## 💡 Pro Tips

1. **Free Tier Limits:**
   - Services spin down after 15 minutes of inactivity
   - First request after spin-down takes ~30 seconds
   - Upgrade to paid plan ($7/month) for always-on service

2. **Environment Variables:**
   - Never commit API keys to GitHub
   - Use Render's environment variable settings
   - Keep `.gitignore` to protect secrets

3. **Auto-Deploy:**
   - Every push to `main` branch auto-deploys
   - You can disable this in settings
   - Manual deploy available in dashboard

4. **Backup:**
   - Your code is on GitHub (backed up)
   - Environment variables are stored in Render
   - Database (if added later) should be backed up separately

---

## ✅ Deployment Checklist

- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Web service created
- [ ] Environment variables set (API keys)
- [ ] Deployment successful
- [ ] App URL working
- [ ] Search functionality tested
- [ ] Eligibility analysis tested
- [ ] Custom domain added (optional)
- [ ] Monitoring set up

---

## 🎉 You're Done!

Your AidLink app is now live on Render! 🚀

**Your App URL:** `https://aidlink.onrender.com` (or your chosen name)

**Next Steps:**
- Share your app with users
- Monitor usage and logs
- Add custom domain (optional)
- Set up alerts for errors

**Need Help?**
- Render Docs: https://render.com/docs
- Render Support: Available in dashboard
- Check logs for specific errors

---

## 📞 Quick Reference

**Render Dashboard:** https://dashboard.render.com
**Your Repository:** https://github.com/Lasp10/aidlink-app
**Render Docs:** https://render.com/docs

**Common Commands:**
- View logs: Dashboard → Your Service → Logs
- Redeploy: Dashboard → Your Service → Manual Deploy
- Update env vars: Dashboard → Your Service → Environment

---

**Happy Deploying! 🎊**

