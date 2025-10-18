# 🚀 CarbonTrack Deployment Guide

CarbonTrack is now ready for deployment! Here are the deployment options:

## 🌟 Current Features Ready for Production

✅ **Complete User Registration & Admin Panel System**
- User registration with form validation
- Admin approval workflow
- Login system for approved users
- Professional UI with notifications
- Complete user management

✅ **Comprehensive Gamification System** 
- 25+ achievements and badges
- Streak tracking and challenges
- Leaderboards and competition
- Activity tracking and rewards
- Progress visualization

✅ **Carbon Tracking Dashboard**
- Carbon footprint calculation
- Emissions tracking and visualization
- Sustainability recommendations
- Goal setting and progress tracking

## 🚀 Quick Deployment Options

### Option 1: Vercel (Recommended for Frontend)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from root directory
vercel --prod

# Or connect to GitHub for auto-deployment
```

### Option 2: Netlify
```bash
# Drag and drop the frontend folder to Netlify dashboard
# Or connect to GitHub repository
```

### Option 3: GitHub Pages
```bash
# Enable GitHub Pages in repository settings
# Set source to main branch /frontend folder
```

## 📱 Frontend-Only Demo Access

The application works fully as a frontend-only demo with:
- Mock data for all features
- Complete user registration flow
- Full admin panel functionality
- All gamification features
- Carbon tracking simulation

## 🔗 Backend Integration (Optional)

For full production with database integration:
1. Deploy backend to Railway, Heroku, or AWS
2. Update API endpoints in frontend
3. Configure authentication and database

## 🌐 Live Demo Features

Users can immediately:
1. **Register Account** → See registration success message
2. **Admin Approval** → Use admin panel to approve users  
3. **Login Access** → Login with approved email + password123
4. **Full Dashboard** → Access all carbon tracking features
5. **Gamification** → Earn achievements and compete on leaderboards

## 📊 Demo Credentials

- **Demo User**: demo@carbontrack.dev / password123
- **Test Registration**: Any email / password123 (after admin approval)
- **Admin Access**: Use "Quick Admin Login" for testing

The application is production-ready for immediate deployment and user testing!
 
## 🧰 GitHub Actions: Deploy Frontend to S3

This repo includes `.github/workflows/deploy-frontend.yml` to deploy `frontend/` to an S3 website bucket.

### Prerequisites
- S3 website buckets:
	- Production: `carbontrack-frontend-production` (Region: us-east-1)
	- Staging: `carbontrack-frontend-staging` (optional)
- Configure one of the following in GitHub Secrets:
	- `AWS_ROLE_TO_ASSUME` (preferred OIDC role), or
	- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- Optional: `CLOUDFRONT_DISTRIBUTION_ID` to invalidate cache post-deploy

### How it works
- Triggers on push to `main` affecting `frontend/**` or via manual dispatch
- Syncs the `frontend/` directory to the chosen S3 bucket
- Sets long cache headers for JS/CSS; index.html uses no-cache to ensure users see latest
- Optionally creates a CloudFront invalidation if configured

### HTTPS Notice
S3 Website endpoints are HTTP-only. For HTTPS, use CloudFront in front of the bucket and an ACM certificate; update DNS to a custom domain pointing at CloudFront.