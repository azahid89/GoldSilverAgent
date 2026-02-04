# Free Deployment Guide for Gold & Silver Agent

This guide covers deploying both the backend (Flask) and frontend (React) for **FREE** using reliable hosting services.

## 🎯 Recommended Setup

- **Backend (Flask)**: [Render.com](https://render.com) - Free tier available
- **Frontend (React)**: [Vercel](https://vercel.com) - Free tier, excellent for React

---

## 📦 Part 1: Backend Deployment (Render.com)

### Why Render?
- ✅ Free tier with 750 hours/month (enough for 24/7)
- ✅ Automatic HTTPS
- ✅ Easy environment variable management
- ✅ Auto-deploy from GitHub
- ✅ No credit card required for free tier

### Step 1: Prepare Your Backend

1. **Create a `Procfile`** (already created in this repo):
   ```
   web: gunicorn api_server:app
   ```

2. **Update `requirements.txt`** to include `gunicorn`:
   ```
   gunicorn>=21.2.0
   ```

3. **Update CORS settings** in `api_server.py` (already done):
   ```python
   CORS(app, resources={r"/api/*": {"origins": ["*"]}})  # For production, specify your frontend URL
   ```

### Step 2: Deploy to Render

1. **Push your code to GitHub** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/gold-silver-agent.git
   git push -u origin main
   ```

2. **Sign up at Render.com**:
   - Go to https://render.com
   - Sign up with GitHub (free)

3. **Create a New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select your repository

4. **Configure the Service**:
   - **Name**: `gold-silver-agent-api` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn api_server:app`
   - **Plan**: Free

5. **Add Environment Variables**:
   Click "Environment" tab and add:
   ```
   FRED_API_KEY=your_fred_api_key
   OPENAI_API_KEY=your_openai_api_key
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key (if using)
   NASDAQ_DATA_LINK_API_KEY=your_nasdaq_key (if using)
   ```

6. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Your backend will be at: `https://your-service-name.onrender.com`

### Step 3: Test Your Backend

Visit: `https://your-service-name.onrender.com/api/health`

You should see: `{"status": "healthy", ...}`

---

## 🎨 Part 2: Frontend Deployment (Vercel)

### Why Vercel?
- ✅ Free tier with excellent performance
- ✅ Automatic HTTPS
- ✅ Instant deployments
- ✅ Built-in CI/CD
- ✅ Perfect for React apps

### Step 1: Prepare Your Frontend

1. **Update API URL** in frontend to use environment variable:
   - Create `.env.production` file (see below)
   - Update API calls to use `process.env.REACT_APP_API_URL`

2. **Build your React app**:
   ```bash
   cd frontend
   npm run build
   ```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI (Recommended)

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd frontend
   vercel
   ```
   - Follow prompts
   - Set project name
   - Set build command: `npm run build`
   - Set output directory: `build`

#### Option B: Using Vercel Dashboard

1. **Sign up at Vercel.com**:
   - Go to https://vercel.com
   - Sign up with GitHub (free)

2. **Import Project**:
   - Click "Add New" → "Project"
   - Import your GitHub repository

3. **Configure Project**:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

4. **Add Environment Variables**:
   Click "Environment Variables" and add:
   ```
   REACT_APP_API_URL=https://your-render-service.onrender.com
   ```

5. **Deploy**:
   - Click "Deploy"
   - Wait 2-3 minutes
   - Your frontend will be live!

---

## 🔧 Configuration Files

### Backend: `Procfile`
```
web: gunicorn api_server:app --bind 0.0.0.0:$PORT
```

### Frontend: `.env.production`
Create `frontend/.env.production`:
```
REACT_APP_API_URL=https://your-render-service.onrender.com
```

### Frontend: `vercel.json` (Optional)
Create `frontend/vercel.json`:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

---

## 🌐 Alternative Free Options

### Backend Alternatives:

1. **Railway.app** (Free tier with $5 credit/month)
   - Similar to Render
   - Good for Flask apps
   - Website: https://railway.app

2. **Fly.io** (Free tier available)
   - Good for containerized apps
   - Website: https://fly.io

3. **PythonAnywhere** (Free tier)
   - Limited but works
   - Website: https://www.pythonanywhere.com

### Frontend Alternatives:

1. **Netlify** (Free tier)
   - Excellent alternative to Vercel
   - Similar features
   - Website: https://netlify.com

2. **Cloudflare Pages** (Free tier)
   - Fast CDN
   - Good performance
   - Website: https://pages.cloudflare.com

3. **GitHub Pages** (Free)
   - Simple static hosting
   - Requires build step
   - Website: https://pages.github.com

---

## 🔒 Security Considerations

### For Production:

1. **Update CORS** in `api_server.py`:
   ```python
   CORS(app, resources={
       r"/api/*": {
           "origins": ["https://your-frontend.vercel.app"],
           "methods": ["GET", "POST"],
           "allow_headers": ["Content-Type"]
       }
   })
   ```

2. **Use Environment Variables**:
   - Never commit API keys
   - Use `.env` files (already in `.gitignore`)

3. **Rate Limiting** (Optional):
   Consider adding rate limiting for production:
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app=app, key_func=get_remote_address)
   ```

---

## 📝 Quick Deployment Checklist

### Backend (Render):
- [ ] Code pushed to GitHub
- [ ] `Procfile` created
- [ ] `gunicorn` in requirements.txt
- [ ] Environment variables set in Render dashboard
- [ ] Service deployed and tested
- [ ] Health endpoint working

### Frontend (Vercel):
- [ ] `.env.production` created with API URL
- [ ] Code pushed to GitHub
- [ ] Vercel project connected
- [ ] Environment variables set
- [ ] Build successful
- [ ] Frontend accessible and API calls working

---

## 🐛 Troubleshooting

### Backend Issues:

1. **"Application failed to respond"**:
   - Check that `gunicorn` is in requirements.txt
   - Verify start command: `gunicorn api_server:app`
   - Check logs in Render dashboard

2. **"Module not found"**:
   - Ensure all dependencies in requirements.txt
   - Check Python version (should be 3.9+)

3. **"Port binding error"**:
   - Use `$PORT` environment variable in Procfile
   - Render sets PORT automatically

### Frontend Issues:

1. **"API calls failing"**:
   - Check `REACT_APP_API_URL` is set correctly
   - Verify CORS settings in backend
   - Check browser console for errors

2. **"Build fails"**:
   - Run `npm install` locally first
   - Check for TypeScript/ESLint errors
   - Verify Node version (should be 16+)

3. **"404 on refresh"**:
   - Add `vercel.json` with proper routing
   - Or configure redirects in Vercel dashboard

---

## 💡 Pro Tips

1. **Custom Domain** (Optional):
   - Both Render and Vercel support custom domains
   - Free SSL certificates included

2. **Monitoring**:
   - Use Render's built-in logs
   - Vercel provides analytics (paid feature)

3. **Auto-Deploy**:
   - Both services auto-deploy on git push
   - No manual deployment needed

4. **Free Tier Limits**:
   - Render: 750 hours/month (enough for 24/7)
   - Vercel: Unlimited bandwidth (generous limits)
   - Both: Sleep after inactivity (Render free tier)

---

## 🚀 Next Steps

1. Deploy backend to Render
2. Deploy frontend to Vercel
3. Test all functionality
4. Share your live app! 🎉

---

## 📞 Need Help?

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Flask Deployment: https://flask.palletsprojects.com/en/latest/deploying/

---

**Happy Deploying! 🚀**

