# 🔌 API Documentation

Complete reference for CarbonTrack's RESTful API, enabling seamless integration with third-party applications and custom implementations.

---

## 🚀 **Getting Started**

### **Base URL**
```
Production: https://api.carbontrack.com/v1
Staging: https://staging-api.carbontrack.com/v1
Development: http://localhost:8000/api/v1
```

### **Authentication**
All API requests require authentication via JWT tokens.

```bash
# Include token in Authorization header
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.carbontrack.com/v1/users/profile
```

### **Response Format**
All responses are in JSON format with consistent structure:

```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Operation successful",
  "timestamp": "2025-09-30T10:00:00Z"
}
```

### **Error Handling**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Invalid email format"]
    }
  },
  "timestamp": "2025-09-30T10:00:00Z"
}
```

---

## 🔐 **Authentication Endpoints**

### **Register User**
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "organization": "Acme Corp"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "user_123",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  }
}
```

### **Login**
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### **Refresh Token**
```http
POST /auth/refresh
Authorization: Bearer {refresh_token}
```

### **Logout**
```http
POST /auth/logout
Authorization: Bearer {access_token}
```

---

## 👤 **User Management**

### **Get User Profile**
```http
GET /users/profile
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "organization": "Acme Corp",
    "role": "user",
    "created_at": "2025-01-01T00:00:00Z",
    "preferences": {
      "units": "metric",
      "notifications": true,
      "privacy_level": "public"
    }
  }
}
```

### **Update Profile**
```http
PUT /users/profile
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Smith",
  "organization": "New Corp",
  "preferences": {
    "units": "imperial",
    "notifications": false
  }
}
```

### **Get User Statistics**
```http
GET /users/stats
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_emissions": 1250.5,
    "monthly_emissions": 85.2,
    "entries_count": 45,
    "goals_completed": 3,
    "achievements_earned": 12,
    "streak_days": 15,
    "rank_position": 42
  }
}
```

---

## 🌍 **Carbon Tracking**

### **Add Carbon Emission**
```http
POST /carbon/emissions
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "category": "transportation",
  "activity_type": "car_petrol",
  "amount": 50.5,
  "unit": "km",
  "date": "2025-09-30",
  "description": "Daily commute to office",
  "metadata": {
    "fuel_type": "petrol",
    "vehicle_size": "medium",
    "passengers": 1
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "emission_456",
    "category": "transportation",
    "activity_type": "car_petrol",
    "amount": 50.5,
    "unit": "km",
    "co2_equivalent": 12.62,
    "date": "2025-09-30",
    "created_at": "2025-09-30T10:00:00Z"
  }
}
```

### **Get Emissions**
```http
GET /carbon/emissions?start_date=2025-09-01&end_date=2025-09-30&category=transportation
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `start_date` (optional): Filter from date (YYYY-MM-DD)
- `end_date` (optional): Filter to date (YYYY-MM-DD)
- `category` (optional): Filter by category
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
{
  "success": true,
  "data": {
    "emissions": [
      {
        "id": "emission_456",
        "category": "transportation",
        "activity_type": "car_petrol",
        "amount": 50.5,
        "unit": "km",
        "co2_equivalent": 12.62,
        "date": "2025-09-30"
      }
    ],
    "total_count": 45,
    "total_co2": 1250.5
  }
}
```

### **Update Emission**
```http
PUT /carbon/emissions/{emission_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "amount": 45.0,
  "description": "Updated commute distance"
}
```

### **Delete Emission**
```http
DELETE /carbon/emissions/{emission_id}
Authorization: Bearer {access_token}
```

### **Calculate CO2 Equivalent**
```http
POST /carbon/calculate
Content-Type: application/json

{
  "category": "transportation",
  "activity_type": "car_petrol",
  "amount": 100,
  "unit": "km",
  "region": "EU"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "co2_equivalent": 25.24,
    "unit": "kg_co2",
    "emission_factor": 0.2524,
    "calculation_method": "IPCC_2021",
    "region": "EU"
  }
}
```

---

## 🎯 **Goals Management**

### **Create Goal**
```http
POST /goals
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Reduce monthly emissions by 20%",
  "description": "Lower my carbon footprint through better transportation choices",
  "goal_type": "emission_reduction",
  "target_value": 20.0,
  "target_unit": "percentage",
  "category": "transportation",
  "start_date": "2025-10-01",
  "end_date": "2025-10-31",
  "priority": "high"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "goal_789",
    "title": "Reduce monthly emissions by 20%",
    "goal_type": "emission_reduction",
    "target_value": 20.0,
    "current_progress": 0.0,
    "status": "active",
    "created_at": "2025-09-30T10:00:00Z"
  }
}
```

### **Get Goals**
```http
GET /goals?status=active&category=transportation
Authorization: Bearer {access_token}
```

### **Update Goal Progress**
```http
PUT /goals/{goal_id}/progress
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "current_progress": 15.5,
  "notes": "Good progress this week"
}
```

---

## 🎮 **Gamification**

### **Get User Achievements**
```http
GET /gamification/achievements
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "earned_achievements": [
      {
        "id": "achievement_first_steps",
        "title": "First Steps",
        "description": "Complete your profile",
        "category": "onboarding",
        "points": 50,
        "earned_at": "2025-09-30T10:00:00Z"
      }
    ],
    "available_achievements": [
      {
        "id": "achievement_daily_tracker",
        "title": "Daily Tracker",
        "description": "Log activities for 7 consecutive days",
        "category": "consistency",
        "points": 200,
        "progress": 3,
        "target": 7
      }
    ],
    "total_points": 350
  }
}
```

### **Get Leaderboards**
```http
GET /gamification/leaderboards?period=monthly&category=overall&limit=10
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "leaderboard": [
      {
        "rank": 1,
        "user": {
          "id": "user_456",
          "name": "Jane Smith",
          "avatar_url": "https://..."
        },
        "points": 2150,
        "co2_reduction": 45.2
      }
    ],
    "user_rank": 15,
    "user_points": 850
  }
}
```

### **Get Active Challenges**
```http
GET /gamification/challenges?status=active
Authorization: Bearer {access_token}
```

### **Join Challenge**
```http
POST /gamification/challenges/{challenge_id}/join
Authorization: Bearer {access_token}
```

---

## 📊 **Analytics & Reporting**

### **Get Dashboard Data**
```http
GET /analytics/dashboard?period=monthly
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_emissions": 1250.5,
      "period_emissions": 85.2,
      "reduction_percentage": -15.3,
      "goal_progress": 75.0
    },
    "breakdown_by_category": [
      {
        "category": "transportation",
        "emissions": 45.2,
        "percentage": 53.1
      },
      {
        "category": "energy",
        "emissions": 25.8,
        "percentage": 30.3
      }
    ],
    "timeline": [
      {
        "date": "2025-09-01",
        "emissions": 2.8
      }
    ]
  }
}
```

### **Get Recommendations**
```http
GET /analytics/recommendations
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "id": "rec_001",
        "category": "transportation",
        "title": "Switch to public transport",
        "description": "Using public transport for your daily commute could reduce emissions by 65%",
        "potential_reduction": 28.5,
        "difficulty": "easy",
        "cost_impact": "save",
        "priority": "high"
      }
    ]
  }
}
```

### **Export Data**
```http
GET /analytics/export?format=csv&start_date=2025-01-01&end_date=2025-12-31
Authorization: Bearer {access_token}
```

---

## 👑 **Admin Endpoints**

### **Get All Users** (Admin Only)
```http
GET /admin/users?status=pending&limit=50
Authorization: Bearer {admin_access_token}
```

### **Approve User Registration** (Admin Only)
```http
POST /admin/users/{user_id}/approve
Authorization: Bearer {admin_access_token}
```

### **System Statistics** (Admin Only)
```http
GET /admin/stats
Authorization: Bearer {admin_access_token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 1250,
    "active_users": 856,
    "pending_registrations": 15,
    "total_emissions_tracked": 125000.5,
    "goals_completed": 450,
    "achievements_earned": 2800
  }
}
```

---

## 🔧 **Utility Endpoints**

### **Get Emission Factors**
```http
GET /utilities/emission-factors?category=transportation&region=EU
```

### **Get Activity Types**
```http
GET /utilities/activity-types?category=energy
```

### **Health Check**
```http
GET /health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 86400,
    "database": "connected",
    "services": {
      "authentication": "operational",
      "calculations": "operational",
      "notifications": "operational"
    }
  }
}
```

---

## 📝 **Rate Limits**

### **Default Limits**
- **Free Tier**: 100 requests/hour
- **Basic Tier**: 1,000 requests/hour  
- **Pro Tier**: 10,000 requests/hour
- **Enterprise**: Custom limits

### **Rate Limit Headers**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1696156800
```

---

## 🔔 **Webhooks**

### **Webhook Events**
- `user.created` - New user registration
- `emission.added` - New emission entry
- `goal.completed` - Goal achievement
- `achievement.earned` - New achievement
- `challenge.completed` - Challenge completion

### **Webhook Payload Example**
```json
{
  "event": "goal.completed",
  "timestamp": "2025-09-30T10:00:00Z",
  "data": {
    "user_id": "user_123",
    "goal_id": "goal_789",
    "goal_title": "Reduce monthly emissions by 20%",
    "completion_percentage": 100
  }
}
```

---

## 📚 **SDKs & Libraries**

### **Official SDKs**
- **JavaScript/TypeScript**: `npm install carbontrack-js`
- **Python**: `pip install carbontrack-python`
- **PHP**: `composer require carbontrack/php-sdk`

### **JavaScript SDK Example**
```javascript
import CarbonTrack from 'carbontrack-js';

const client = new CarbonTrack({
  apiKey: 'your-api-key',
  environment: 'production'
});

// Add emission
const emission = await client.emissions.create({
  category: 'transportation',
  activity_type: 'car_petrol',
  amount: 50.5,
  unit: 'km'
});

// Get user stats
const stats = await client.users.getStats();
```

---

## ❓ **Support**

### **Getting Help**
- **Documentation**: [API Docs](https://docs.carbontrack.com)
- **Support Email**: api-support@carbontrack.com
- **Developer Forum**: [GitHub Discussions](https://github.com/ahmedul/CarbonTrack/discussions)
- **Status Page**: [status.carbontrack.com](https://status.carbontrack.com)

### **API Changelog**
- **v1.2.0** (2025-09-30): Added webhook support
- **v1.1.0** (2025-09-15): Enhanced gamification endpoints
- **v1.0.0** (2025-09-01): Initial API release

---

**Ready to integrate with CarbonTrack?** [**Get your API key →**](https://ahmedul.github.io/CarbonTrack/)

*Build the future of carbon management* 🚀🌱