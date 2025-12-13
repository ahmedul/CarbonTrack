# CarbonTrack Frontend

A Vue.js 3 frontend application for tracking carbon emissions with enterprise CSRD compliance features.

## Features

- 🌍 **Carbon Tracking**: Log and monitor your carbon emissions across 5 major categories
- 📊 **Interactive Dashboard**: Real-time charts with trend analysis and goal tracking
- 🎯 **Goals & Achievements**: Gamification system with badges, streaks, and leaderboards
- 💡 **AI Recommendations**: Personalized carbon reduction strategies with ROI calculations
- 👥 **Multi-User Support**: Team collaboration with role-based access control
- 🏆 **Gamification**: 30+ achievements, team challenges, and points system
- 🆕 **CSRD Compliance**: EU regulatory reporting (launching Q1 2026)
- 🔐 **Authentication**: Secure AWS Cognito integration with JWT tokens

## Technology Stack

- **Vue.js 3** - Progressive JavaScript framework (CDN-based, no build required)
- **Tailwind CSS** - Utility-first CSS framework with custom gradient designs
- **Chart.js** - Interactive data visualization with real-time updates
- **Axios** - HTTP client for REST API communication
- **AWS CloudFront** - Global CDN with HTTPS, compression, and edge caching
- **S3 Static Hosting** - Production deployment with 99.9% uptime

## Quick Start

### Prerequisites

- Python 3.x (for development server)
- Running CarbonTrack backend API (port 8000)

### Development Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Start the development server:
   ```bash
   npm run dev
   # or
   python3 -m http.server 3000
   ```

3. Open your browser and visit: `http://localhost:3000`

## Project Structure

```
frontend/
├── index.html          # Main landing page with CSRD branding
├── app-full.js         # Complete Vue.js application with all features
├── app-simple.js       # Simplified version for testing
├── app.js              # Core application logic
├── landing.html        # Marketing landing page (NEW)
├── package.json        # Project configuration
└── README.md           # This file
```

## API Integration

The frontend connects to the production FastAPI backend:

**Production API**: `https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod`

### Core Endpoints
- **Authentication**: `/api/v1/auth/*` - Login, register, token refresh
- **Carbon Tracking**: `/api/v1/carbon-emissions/*` - CRUD operations for emissions
- **Analytics**: `/api/v1/carbon-emissions/analytics` - Trend analysis and insights
- **Goals**: `/api/v1/goals/*` - Carbon reduction goal management
- **Achievements**: `/api/v1/achievements/*` - Track user milestones

### Gamification Endpoints
- **Profile**: `/api/v1/gamification/profile` - User stats, points, level
- **Achievements**: `/api/v1/gamification/achievements` - Badge progress
- **Leaderboards**: `/api/v1/gamification/leaderboards` - Rankings and competitions

### AI Recommendations
- **Get Recommendations**: `/api/v1/recommendations/` - Personalized strategies
- **Stats**: `/api/v1/recommendations/stats` - Recommendation effectiveness

### 🆕 CSRD Compliance (Q1 2026)
- **Reports**: `/api/v1/csrd/reports` - Create, manage CSRD reports
- **Emissions Data**: `/api/v1/csrd/reports/{id}/emissions` - Scope 1/2/3 tracking
- **ESRS Metrics**: `/api/v1/csrd/reports/{id}/esrs-metrics` - Environmental standards
- **Export**: `/api/v1/csrd/reports/{id}/export/pdf` - PDF/XBRL generation
- **Validation**: `/api/v1/csrd/reports/{id}/validate` - Compliance checking

## Features Overview

### 🏠 Dashboard
- Real-time emission statistics (monthly, yearly, total)
- Interactive Chart.js visualizations with trend lines
- Goal progress tracking with visual indicators
- Recent activity feed with category breakdowns
- Carbon intensity metrics (kg CO2e per day/month)

### ➕ Add Emissions
- 5 major categories: Transportation, Energy, Food, Waste, Operations
- 80+ activity types with scientific emission factors (EPA, IPCC, DEFRA)
- Automatic CO₂ equivalent calculations
- Unit conversion support (km/miles, kWh, liters, kg)
- Bulk import via CSV (coming soon)

### 👤 Profile Management
- Personal information and preferences
- Carbon budget setting with alerts
- Goal configuration and tracking
- Usage statistics and achievements
- Team management (multi-user)

### 🎮 Gamification System
- **30+ Achievements**: First Entry, Green Commuter, Carbon Neutral Month, etc.
- **Points & Levels**: Earn XP for sustainable actions
- **Streaks**: Daily/weekly tracking momentum
- **Leaderboards**: Compete with friends and teams
- **Challenges**: Weekly/monthly reduction targets

### 💡 AI-Powered Recommendations
- Personalized carbon reduction strategies
- Scientific backing from peer-reviewed research
- Cost-benefit analysis with ROI calculations
- Implementation step-by-step guides
- Priority scoring based on your footprint patterns

### 🆕 CSRD Compliance Module (Q1 2026)
- **ESRS E1 Reporting**: Climate change disclosures
- **Scope 1/2/3 Categorization**: Automatic emission classification
- **PDF Export**: Professional audit-ready reports
- **XBRL Format**: Regulatory filing compliance
- **Multi-Year Trends**: Historical analysis and forecasting
- **Deadline Tracking**: Compliance calendar with alerts
- **Audit Trail**: Full history for third-party verification

### 🔐 Authentication
- Secure AWS Cognito integration
- JWT token-based sessions
- Persistent login state
- Secure logout functionality

## Development Notes

This frontend uses CDN-based Vue.js (no build process) for maximum simplicity and compatibility. The application is production-ready with:

- **Zero Build Step**: Deploy static files directly to S3
- **CloudFront CDN**: Global edge caching with HTTPS
- **Gzip/Brotli Compression**: 70% smaller file sizes
- **SPA Routing**: CloudFront handles 403/404 → index.html
- **API Gateway Integration**: CORS-enabled REST API
- **JWT Authentication**: Secure token-based sessions

### Production URLs

- **CloudFront**: https://d2z2og1o0b9esb.cloudfront.net
- **Custom Domain**: carbontracksystem.com (launching Q1 2026)
- **API**: https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod
- **Region**: eu-central-1 (Frankfurt)

### Performance Metrics

- **First Load**: <2s globally (CloudFront edge caching)
- **API Response**: <200ms average
- **Uptime**: 99.9% SLA
- **CDN Locations**: 400+ global edge locations

## Browser Support

- Chrome/Chromium (recommended) - Full support
- Firefox - Full support
- Safari - Full support  
- Edge - Full support
- Mobile browsers - Responsive design

## Deployment

### Production Deployment (Current)

```bash
# Upload to S3
aws s3 sync . s3://carbontrack-frontend --exclude ".*" --exclude "README.md"

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id EUKA4HQFK6MC \
  --paths "/*"
```

### Local Development

```bash
# Simple HTTP server
python3 -m http.server 3000

# Or use any static file server
npx serve -p 3000
```

No build process, no dependencies to install!