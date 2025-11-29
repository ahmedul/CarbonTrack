#!/bin/bash

# Script to integrate CSRD dashboard into main frontend application
# Run this after deploying the CSRD module to production

set -e

echo "🔧 Integrating CSRD Dashboard into Frontend"
echo "==========================================="
echo ""

FRONTEND_DIR="/home/akabir/git/my-projects/CarbonTrack/frontend"
BACKUP_DIR="/tmp/carbontrack-backup-$(date +%Y%m%d-%H%M%S)"

# Backup current frontend
echo "📦 Creating backup..."
mkdir -p "$BACKUP_DIR"
cp "$FRONTEND_DIR/app-full.js" "$BACKUP_DIR/app-full.js.backup"
cp "$FRONTEND_DIR/index.html" "$BACKUP_DIR/index.html.backup"
echo "   ✅ Backup created at: $BACKUP_DIR"
echo ""

# Add CSRD CSS to index.html
echo "🎨 Adding CSRD CSS to index.html..."
if grep -q "csrd-dashboard.css" "$FRONTEND_DIR/index.html"; then
    echo "   ℹ️  CSRD CSS already included"
else
    # Find the last stylesheet link and add CSRD CSS after it
    sed -i '/<link rel="stylesheet" href="styles.css">/a \    <link rel="stylesheet" href="csrd-dashboard.css">' "$FRONTEND_DIR/index.html"
    echo "   ✅ CSRD CSS added to index.html"
fi
echo ""

# Add CSRD JS to index.html
echo "📜 Adding CSRD JS to index.html..."
if grep -q "csrd-dashboard.js" "$FRONTEND_DIR/index.html"; then
    echo "   ℹ️  CSRD JS already included"
else
    # Find app-full.js and add CSRD JS before it
    sed -i '/<script src="app-full.js"><\/script>/i \    <script src="csrd-dashboard.js"></script>' "$FRONTEND_DIR/index.html"
    echo "   ✅ CSRD JS added to index.html"
fi
echo ""

echo "📝 Next manual steps:"
echo ""
echo "1. Add CSRD navigation item to app-full.js:"
echo "   Find the 'navigationItems' array and add:"
echo ""
echo "   {
    id: 'csrd',
    name: 'CSRD Compliance',
    icon: 'fa-chart-bar',
    component: 'csrd-dashboard',
    requiresAuth: true,
    badge: 'PREMIUM'
  }"
echo ""
echo "2. Register CSRD component in app-full.js:"
echo "   Add to components section:"
echo ""
echo "   'csrd-dashboard': CSRDDashboard"
echo ""
echo "3. Add subscription check:"
echo "   Update checkSubscriptionAccess() to include CSRD"
echo ""
echo "4. Test locally:"
echo "   cd frontend && python3 -m http.server 8080"
echo "   Open http://localhost:8080"
echo ""
echo "5. Deploy to S3:"
echo "   aws s3 sync . s3://carbontrack-frontend-production/ --delete"
echo "   aws cloudfront create-invalidation --distribution-id EUKA4HQFK6MC --paths '/*'"
echo ""
echo "✅ Integration script complete!"
echo ""
echo "💡 Rollback command if needed:"
echo "   cp $BACKUP_DIR/app-full.js.backup $FRONTEND_DIR/app-full.js"
echo "   cp $BACKUP_DIR/index.html.backup $FRONTEND_DIR/index.html"
