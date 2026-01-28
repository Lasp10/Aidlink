# AidLink Domain Connection & Deployment Guide

This guide will help you deploy your AidLink Flask application and connect it to a custom domain.

## 🚀 Quick Start Options

### Option 1: Render (Recommended - Easiest)
**Best for**: Quick deployment with automatic SSL and domain support

### Option 2: Railway
**Best for**: Simple deployments with Docker support

### Option 3: DigitalOcean App Platform
**Best for**: More control and scalability

### Option 4: Heroku
**Best for**: Traditional PaaS (note: free tier discontinued)

### Option 5: AWS/GCP/Azure
**Best for**: Enterprise-scale deployments

---

## 📋 Pre-Deployment Checklist

1. ✅ **Domain purchased** (from Namecheap, GoDaddy, Google Domains, etc.)
2. ✅ **API keys ready**:
   - `GOOGLE_PLACES_API_KEY`
   - `GEMINI_API_KEY`
3. ✅ **Code committed** to Git (GitHub, GitLab, or Bitbucket)

---

## 🎯 Option 1: Deploy to Render (Recommended)

### Step 1: Prepare Your Repository
```bash
# Make sure your code is pushed to GitHub/GitLab/Bitbucket
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub/GitLab
3. Click "New +" → "Web Service"

### Step 3: Connect Repository
1. Select your AidLink repository
2. Configure:
   - **Name**: `aidlink` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn AIDLINK.dynamic_app:app --bind 0.0.0.0:$PORT`
   - **Root Directory**: Leave empty (or set to `AIDLINK/` if you want)

### Step 4: Set Environment Variables
In Render dashboard, go to "Environment" tab and add:
```
GOOGLE_PLACES_API_KEY=your_actual_key_here
GEMINI_API_KEY=your_actual_key_here
PORT=10000
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for build to complete (5-10 minutes)
3. Your app will be live at: `https://aidlink.onrender.com`

### Step 6: Connect Custom Domain
1. In Render dashboard, go to "Settings" → "Custom Domains"
2. Click "Add Custom Domain"
3. Enter your domain (e.g., `aidlink.com` or `www.aidlink.com`)
4. Render will provide DNS records to add:
   - **CNAME**: `aidlink.onrender.com` (for www subdomain)
   - **A Record**: Render's IP address (for root domain)

### Step 7: Configure DNS
Go to your domain registrar (Namecheap, GoDaddy, etc.):

**For www subdomain:**
- Type: `CNAME`
- Name: `www`
- Value: `aidlink.onrender.com`
- TTL: `3600`

**For root domain (apex):**
- Type: `A`
- Name: `@` (or leave blank)
- Value: `[IP from Render]`
- TTL: `3600`

### Step 8: SSL Certificate
- Render automatically provisions SSL certificates via Let's Encrypt
- Wait 24-48 hours for DNS propagation
- SSL will activate automatically

---

## 🚂 Option 2: Deploy to Railway

### Step 1: Install Railway CLI
```bash
npm i -g @railway/cli
railway login
```

### Step 2: Initialize Project
```bash
cd /Users/_an.kith/Desktop/My_Apps/AIDLINK
railway init
railway up
```

### Step 3: Set Environment Variables
```bash
railway variables set GOOGLE_PLACES_API_KEY=your_key
railway variables set GEMINI_API_KEY=your_key
railway variables set PORT=8000
```

### Step 4: Deploy
```bash
railway up
```

### Step 5: Add Custom Domain
1. Go to Railway dashboard → Your project → Settings
2. Click "Generate Domain" or "Add Custom Domain"
3. Enter your domain
4. Add DNS records as shown in Railway dashboard

---

## 🐳 Option 3: Deploy with Docker (Any Platform)

### Step 1: Build Docker Image
```bash
cd /Users/_an.kith/Desktop/My_Apps/AIDLINK
docker build -f AIDLINK/Dockerfile -t aidlink:latest .
```

### Step 2: Test Locally
```bash
docker run -p 8000:8000 \
  -e GOOGLE_PLACES_API_KEY=your_key \
  -e GEMINI_API_KEY=your_key \
  aidlink:latest
```

### Step 3: Push to Registry
```bash
# Tag for your registry (Docker Hub, AWS ECR, etc.)
docker tag aidlink:latest yourusername/aidlink:latest
docker push yourusername/aidlink:latest
```

### Step 4: Deploy to Platform
- **DigitalOcean App Platform**: Use Dockerfile option
- **AWS ECS/Fargate**: Use container registry
- **Google Cloud Run**: Deploy container directly

---

## 🌐 DNS Configuration Guide

### Understanding DNS Records

**A Record** (Address Record):
- Points domain to IP address
- Use for root domain: `example.com`

**CNAME Record** (Canonical Name):
- Points domain to another domain
- Use for subdomains: `www.example.com`

**Example DNS Setup:**

```
Type    Name    Value                    TTL
A       @       192.0.2.1                3600
CNAME   www     aidlink.onrender.com     3600
```

### Common Domain Registrars

**Namecheap:**
1. Login → Domain List → Manage
2. Advanced DNS → Add New Record
3. Enter type, host, value, TTL
4. Save

**GoDaddy:**
1. My Products → DNS
2. Add Record
3. Select type, enter name and value
4. Save

**Google Domains:**
1. DNS → Custom Records
2. Add record
3. Enter type, name, data
4. Save

---

## 🔒 SSL/HTTPS Setup

### Automatic SSL (Recommended)
Most platforms (Render, Railway, Vercel, Netlify) automatically provide SSL:
- ✅ Let's Encrypt certificates
- ✅ Auto-renewal
- ✅ No configuration needed

### Manual SSL (If Needed)
If using VPS or custom server:
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (already configured)
sudo certbot renew --dry-run
```

---

## ⚙️ Production Configuration

### Update Flask App for Production

You may need to update `AIDLINK/dynamic_app.py`:

```python
# At the bottom of dynamic_app.py, update main():
def main():
    port = int(os.getenv('PORT', 8000))
    # Disable debug in production
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
```

### Update CORS Settings (if needed)
```python
# In dynamic_app.py, update CORS:
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com", "https://www.yourdomain.com"]
    }
})
```

### Environment Variables for Production
Set these in your hosting platform:
```
GOOGLE_PLACES_API_KEY=your_key
GEMINI_API_KEY=your_key
PORT=8000
DEBUG=False
FLASK_ENV=production
```

---

## 🧪 Testing Your Deployment

### 1. Test API Endpoints
```bash
# Status check
curl https://yourdomain.com/api/status

# Search test
curl -X POST https://yourdomain.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "food assistance", "location": "Sacramento, CA"}'
```

### 2. Test Frontend
- Visit `https://yourdomain.com`
- Try a search
- Check browser console for errors

### 3. Test SSL
- Visit [SSL Labs](https://www.ssllabs.com/ssltest/)
- Enter your domain
- Check for A+ rating

---

## 🔧 Troubleshooting

### Issue: Domain not resolving
**Solution:**
- Wait 24-48 hours for DNS propagation
- Check DNS with: `dig yourdomain.com` or `nslookup yourdomain.com`
- Verify DNS records are correct

### Issue: SSL certificate not working
**Solution:**
- Ensure DNS is fully propagated
- Check platform's SSL status in dashboard
- Try regenerating certificate

### Issue: App not loading
**Solution:**
- Check application logs in hosting dashboard
- Verify environment variables are set
- Ensure PORT is correctly configured
- Check build logs for errors

### Issue: API calls failing
**Solution:**
- Verify API keys are set correctly
- Check CORS settings
- Review application logs

---

## 📊 Recommended Hosting Comparison

| Platform | Free Tier | Custom Domain | SSL | Ease of Use | Best For |
|----------|-----------|---------------|-----|-------------|----------|
| **Render** | ✅ Yes | ✅ Free | ✅ Auto | ⭐⭐⭐⭐⭐ | Beginners |
| **Railway** | ✅ Yes | ✅ Free | ✅ Auto | ⭐⭐⭐⭐ | Docker users |
| **Vercel** | ✅ Yes | ✅ Free | ✅ Auto | ⭐⭐⭐⭐⭐ | Frontend-heavy |
| **DigitalOcean** | ❌ No | ✅ Free | ✅ Auto | ⭐⭐⭐ | More control |
| **Heroku** | ❌ No | ✅ Paid | ✅ Auto | ⭐⭐⭐⭐ | Traditional PaaS |
| **AWS** | ❌ No | ✅ Free | ✅ Manual | ⭐⭐ | Enterprise |

---

## 🎯 Quick Deploy Commands

### Render (via CLI)
```bash
# Install Render CLI
npm install -g render-cli

# Login
render login

# Deploy
render deploy
```

### Railway (via CLI)
```bash
railway login
railway init
railway up
```

### Docker + Any Platform
```bash
docker build -t aidlink .
docker run -p 8000:8000 \
  -e GOOGLE_PLACES_API_KEY=key \
  -e GEMINI_API_KEY=key \
  aidlink
```

---

## 📝 Next Steps After Deployment

1. ✅ **Monitor Logs**: Check application logs regularly
2. ✅ **Set Up Monitoring**: Use services like Sentry, LogRocket, or platform's built-in monitoring
3. ✅ **Backup Strategy**: Set up database backups if using persistent storage
4. ✅ **Performance**: Enable CDN if available (Cloudflare, etc.)
5. ✅ **Analytics**: Add Google Analytics or similar
6. ✅ **Domain Email**: Set up email forwarding (e.g., `contact@yourdomain.com`)

---

## 🆘 Need Help?

- **Render Support**: [render.com/docs](https://render.com/docs)
- **Railway Support**: [railway.app/docs](https://railway.app/docs)
- **DNS Issues**: Check with your domain registrar
- **SSL Issues**: Contact your hosting platform support

---

## ✅ Deployment Checklist

- [ ] Code pushed to Git repository
- [ ] Hosting platform account created
- [ ] Application deployed successfully
- [ ] Environment variables configured
- [ ] Custom domain added
- [ ] DNS records configured
- [ ] SSL certificate active
- [ ] Application accessible via custom domain
- [ ] API endpoints tested
- [ ] Frontend tested
- [ ] Monitoring set up

---

**Congratulations!** Your AidLink app should now be live at your custom domain! 🎉


