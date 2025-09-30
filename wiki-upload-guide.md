# 📚 GitHub Wiki Upload Guide

This guide will help you upload the professional wiki documentation to your GitHub repository.

## 🚀 Quick Setup Steps

### Step 1: Enable Wiki on GitHub
1. Go to your repository: https://github.com/ahmedul/CarbonTrack
2. Click on **Settings** tab
3. Scroll down to **Features** section
4. Check ✅ **Wikis** to enable it
5. Click **Save changes**

### Step 2: Create First Wiki Page
1. Go to your repository homepage
2. Click on **Wiki** tab (should appear after enabling)
3. Click **Create the first page**
4. Title: `Home`
5. Copy content from `wiki/Home.md` and paste it
6. Click **Save Page**

### Step 3: Clone Wiki Repository (After Step 2)
```bash
# Navigate to your projects directory
cd /home/akabir/git/my-projects/

# Clone the wiki repository (this will work after creating first page)
git clone https://github.com/ahmedul/CarbonTrack.wiki.git

# Navigate to wiki directory
cd CarbonTrack.wiki/
```

## 📋 Wiki Pages to Create

Here are all the pages you need to create in order:

### 1. Home Page ✅ (Create First)
- **File**: `wiki/Home.md`
- **GitHub Wiki Title**: `Home`
- **Description**: Main landing page with project overview

### 2. Quick Start Guide
- **File**: `wiki/Quick-Start-Guide.md`
- **GitHub Wiki Title**: `Quick-Start-Guide`
- **Description**: 5-minute user onboarding

### 3. Architecture Overview
- **File**: `wiki/Architecture-Overview.md`
- **GitHub Wiki Title**: `Architecture-Overview`
- **Description**: Technical system design

### 4. User Manual
- **File**: `wiki/User-Manual.md`
- **GitHub Wiki Title**: `User-Manual`
- **Description**: Comprehensive feature guide

### 5. Gamification System
- **File**: `wiki/Gamification-System.md`
- **GitHub Wiki Title**: `Gamification-System`
- **Description**: Achievement and engagement system

### 6. Business Model
- **File**: `wiki/Business-Model.md`
- **GitHub Wiki Title**: `Business-Model`
- **Description**: Commercial strategy and market analysis

### 7. API Documentation
- **File**: `wiki/API-Documentation.md`
- **GitHub Wiki Title**: `API-Documentation`
- **Description**: Complete API reference

### 8. Security & Privacy Guide
- **File**: `wiki/Security-Privacy-Guide.md`
- **GitHub Wiki Title**: `Security-Privacy-Guide`
- **Description**: Security and compliance documentation

### 9. Installation & Deployment Guide
- **File**: `wiki/Installation-Deployment-Guide.md`
- **GitHub Wiki Title**: `Installation-Deployment-Guide`
- **Description**: Setup and deployment instructions

## 🔄 Automated Upload Script

After enabling the wiki and creating the first page, run this script:

```bash
#!/bin/bash

echo "📚 Uploading CarbonTrack Wiki Documentation..."

# Clone wiki repository if not exists
if [ ! -d "CarbonTrack.wiki" ]; then
    echo "🔄 Cloning wiki repository..."
    git clone https://github.com/ahmedul/CarbonTrack.wiki.git
fi

cd CarbonTrack.wiki/

# Copy all wiki files
echo "📝 Copying wiki files..."
cp ../CarbonTrack/wiki/Home.md ./Home.md
cp "../CarbonTrack/wiki/Quick-Start-Guide.md" ./Quick-Start-Guide.md
cp "../CarbonTrack/wiki/Architecture-Overview.md" ./Architecture-Overview.md
cp "../CarbonTrack/wiki/User-Manual.md" ./User-Manual.md
cp "../CarbonTrack/wiki/Gamification-System.md" ./Gamification-System.md
cp "../CarbonTrack/wiki/Business-Model.md" ./Business-Model.md
cp "../CarbonTrack/wiki/API-Documentation.md" ./API-Documentation.md
cp "../CarbonTrack/wiki/Security-Privacy-Guide.md" ./Security-Privacy-Guide.md
cp "../CarbonTrack/wiki/Installation-Deployment-Guide.md" ./Installation-Deployment-Guide.md

# Add all files to git
echo "📤 Adding files to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "📚 Add comprehensive CarbonTrack wiki documentation

- Complete user manual and quick start guide
- Technical architecture overview  
- Gamification system documentation
- Business model and market analysis
- Complete API documentation
- Security and privacy guide
- Installation and deployment instructions

Professional documentation for CarbonTrack SaaS platform"

# Push to GitHub
echo "🚀 Pushing to GitHub wiki..."
git push origin master

echo "✅ Wiki documentation uploaded successfully!"
echo "🌐 View your wiki at: https://github.com/ahmedul/CarbonTrack/wiki"
```

## 🎯 Manual Upload Method (Alternative)

If you prefer to upload manually through GitHub's web interface:

### For Each Wiki Page:
1. Go to: https://github.com/ahmedul/CarbonTrack/wiki
2. Click **New Page**
3. Enter the page title (from list above)
4. Open the corresponding `.md` file from the `wiki/` folder
5. Copy all content and paste into GitHub's editor
6. Click **Save Page**
7. Repeat for all 9 pages

## 🔗 Navigation Setup

After uploading all pages, edit the **Home** page to ensure all navigation links work:

- All links in the format `[Page Name](Page-Name)` should work automatically
- GitHub wiki automatically handles the URL routing
- Test all navigation links after upload

## ✨ Final Result

Your professional wiki will be available at:
**https://github.com/ahmedul/CarbonTrack/wiki**

The wiki will include:
- ✅ Professional landing page
- ✅ Complete user documentation
- ✅ Technical architecture details
- ✅ API reference documentation  
- ✅ Business model and strategy
- ✅ Security and compliance info
- ✅ Installation and deployment guides
- ✅ Gamification system details

---

**Need Help?**
- If you encounter any issues, check that the wiki feature is enabled in repository settings
- Ensure you've created the first page through the web interface before cloning
- All markdown formatting will be preserved in the GitHub wiki

**Ready to go live?** 🚀 Follow the steps above to publish your professional documentation!