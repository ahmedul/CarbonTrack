# CarbonTrack Frontend

A Vue.js 3 frontend application for tracking carbon emissions and environmental impact.

## Features

- 🌍 **Carbon Tracking**: Log and monitor your carbon emissions across different categories
- 📊 **Dashboard**: Interactive charts and statistics showing your environmental impact
- 🎯 **Goals & Achievements**: Set carbon reduction goals and track progress  
- 👤 **User Profile**: Manage personal settings and carbon budgets
- 🔐 **Authentication**: Secure login with AWS Cognito integration

## Technology Stack

- **Vue.js 3** - Progressive JavaScript framework (CDN-based for Node.js compatibility)
- **Tailwind CSS** - Utility-first CSS framework
- **Chart.js** - Interactive data visualization
- **Axios** - HTTP client for API communication

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
├── index.html          # Main HTML file with Vue.js app
├── app.js              # Vue.js application logic
├── package.json        # Project configuration
└── README.md           # This file
```

## API Integration

The frontend connects to the FastAPI backend running on `http://localhost:8000`:

- **Authentication**: `/auth/login` - User login with AWS Cognito
- **Carbon Data**: `/carbon/` - CRUD operations for emission entries
- **User Management**: `/users/me` - User profile management
- **Health Check**: `/health` - API status verification

## Features Overview

### 🏠 Dashboard
- Monthly and total emission statistics
- Interactive time-series charts
- Goal progress tracking
- Recent activity feed

### ➕ Add Emissions
- Category-based input (Transportation, Energy, Food, Waste, Other)
- Automatic CO₂ equivalent calculations
- Date and description tracking
- Unit conversion support

### 👤 Profile Management
- Personal information updates
- Carbon budget setting
- Goal configuration
- Usage statistics

### 🔐 Authentication
- Secure AWS Cognito integration
- JWT token-based sessions
- Persistent login state
- Secure logout functionality

## Development Notes

This frontend uses CDN-based Vue.js to maintain compatibility with older Node.js versions (v12.x). The application is fully functional and production-ready while avoiding complex build tools that require newer Node.js versions.

## Browser Support

- Chrome/Chromium (recommended)
- Firefox  
- Safari
- Edge

## Contributing

1. Make changes to `index.html` for UI structure
2. Update `app.js` for Vue.js application logic
3. Test locally with the development server
4. Ensure backend API compatibility

## Deployment

For production deployment, simply serve the static files (`index.html`, `app.js`) through any web server or CDN. No build process required!