#!/bin/bash

# 📚 CarbonTrack Wiki Upload Script
# This script uploads all wiki documentation to GitHub wiki repository

set -e  # Exit on any error

echo "🚀 CarbonTrack Wiki Upload Script"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -d "wiki" ]; then
    echo "❌ Error: wiki directory not found!"
    echo "Please run this script from the CarbonTrack project root directory."
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo "✅ Found wiki directory with documentation"
echo ""

# Check if wiki files exist
WIKI_FILES=(
    "wiki/Home.md"
    "wiki/Quick-Start-Guide.md"
    "wiki/Architecture-Overview.md"
    "wiki/User-Manual.md"
    "wiki/Gamification-System.md"
    "wiki/Business-Model.md"
    "wiki/API-Documentation.md"
    "wiki/Security-Privacy-Guide.md"
    "wiki/Installation-Deployment-Guide.md"
)

echo "🔍 Checking wiki files..."
for file in "${WIKI_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ Missing: $file"
        exit 1
    fi
done
echo ""

# Navigate to parent directory for cloning
cd ..

REPO_NAME="CarbonTrack"
WIKI_URL="https://github.com/ahmedul/CarbonTrack.wiki.git"

echo "🔄 Cloning GitHub wiki repository..."
echo "📍 Wiki URL: $WIKI_URL"

# Remove existing wiki clone if it exists
if [ -d "$REPO_NAME.wiki" ]; then
    echo "🗑️  Removing existing wiki directory..."
    rm -rf "$REPO_NAME.wiki"
fi

# Clone the wiki repository
if git clone "$WIKI_URL" 2>/dev/null; then
    echo "✅ Successfully cloned wiki repository"
else
    echo "❌ Failed to clone wiki repository"
    echo ""
    echo "🛠️  SETUP REQUIRED:"
    echo "1. Go to https://github.com/ahmedul/CarbonTrack"
    echo "2. Click Settings → Features → Enable Wikis ✅"
    echo "3. Go to Wiki tab → Create the first page"
    echo "4. Title: 'Home', Content: any text, Save"
    echo "5. Run this script again"
    echo ""
    exit 1
fi

# Navigate to wiki directory
cd "$REPO_NAME.wiki"
echo "📁 Entered wiki directory: $(pwd)"
echo ""

# Copy wiki files
echo "📝 Copying wiki documentation files..."

# Copy Home page
cp "../$REPO_NAME/wiki/Home.md" "./Home.md"
echo "  ✅ Home.md"

# Copy other pages
cp "../$REPO_NAME/wiki/Quick-Start-Guide.md" "./Quick-Start-Guide.md"
echo "  ✅ Quick-Start-Guide.md"

cp "../$REPO_NAME/wiki/Architecture-Overview.md" "./Architecture-Overview.md"
echo "  ✅ Architecture-Overview.md"

cp "../$REPO_NAME/wiki/User-Manual.md" "./User-Manual.md"
echo "  ✅ User-Manual.md"

cp "../$REPO_NAME/wiki/Gamification-System.md" "./Gamification-System.md"
echo "  ✅ Gamification-System.md"

cp "../$REPO_NAME/wiki/Business-Model.md" "./Business-Model.md"
echo "  ✅ Business-Model.md"

cp "../$REPO_NAME/wiki/API-Documentation.md" "./API-Documentation.md"
echo "  ✅ API-Documentation.md"

cp "../$REPO_NAME/wiki/Security-Privacy-Guide.md" "./Security-Privacy-Guide.md"
echo "  ✅ Security-Privacy-Guide.md"

cp "../$REPO_NAME/wiki/Installation-Deployment-Guide.md" "./Installation-Deployment-Guide.md"
echo "  ✅ Installation-Deployment-Guide.md"

echo ""

# Check git status
echo "📊 Git status:"
git status --porcelain

# Add all files
echo ""
echo "📤 Adding files to git..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes detected. Wiki is already up to date!"
else
    # Commit changes
    echo "💾 Committing changes..."
    git commit -m "📚 Add comprehensive CarbonTrack wiki documentation

✨ Complete professional documentation suite including:

📖 User Documentation:
- Home page with project overview and navigation
- Quick Start Guide (5-minute onboarding)
- User Manual (comprehensive feature guide)

🏗️ Technical Documentation:
- Architecture Overview (system design)
- API Documentation (complete REST API reference)
- Installation & Deployment Guide (dev to production)

🎮 Feature Documentation:
- Gamification System (achievements, leaderboards, challenges)
- Security & Privacy Guide (GDPR compliance, encryption)

💼 Business Documentation:
- Business Model (SaaS strategy, market analysis)

🎯 Key Features:
- Professional formatting with emojis and diagrams
- Code examples and implementation guides
- Comprehensive troubleshooting sections
- Multi-environment setup instructions
- Security best practices and compliance

This documentation positions CarbonTrack as an enterprise-ready
SaaS platform for carbon footprint management and sustainability."

    # Push to GitHub
    echo ""
    echo "🚀 Pushing to GitHub wiki repository..."
    git push origin master
    
    echo ""
    echo "🎉 SUCCESS! Wiki documentation uploaded!"
fi

echo ""
echo "🌐 Your professional wiki is now live at:"
echo "   https://github.com/ahmedul/CarbonTrack/wiki"
echo ""
echo "📚 Documentation includes:"
echo "   ✅ Home page with complete navigation"
echo "   ✅ Quick Start Guide (5-minute setup)"
echo "   ✅ User Manual (comprehensive features)"
echo "   ✅ Architecture Overview (technical design)"
echo "   ✅ API Documentation (complete REST API)"
echo "   ✅ Gamification System (achievements & leaderboards)"
echo "   ✅ Business Model (SaaS strategy & market analysis)"
echo "   ✅ Security & Privacy Guide (GDPR compliance)"
echo "   ✅ Installation & Deployment Guide (dev to production)"
echo ""
echo "🎯 Next steps:"
echo "   1. Visit your wiki and test all navigation links"
echo "   2. Share the wiki URL with users and stakeholders"  
echo "   3. Consider adding screenshots and diagrams"
echo "   4. Set up automatic wiki updates in CI/CD"
echo ""
echo "🚀 Your CarbonTrack documentation is now professional and complete!"