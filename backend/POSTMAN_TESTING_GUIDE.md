# 🚀 CarbonTrack API Testing Guide with Postman

## 📋 Setup Instructions

### 1. Import the Postman Collection
1. Open Postman
2. Click **Import** button
3. Select the file: `CarbonTrack_Postman_Collection.json`
4. The collection will be imported with all endpoints organized by categories

### 2. Environment Variables
The collection uses these variables (automatically configured):
- `base_url`: http://localhost:8000
- `access_token`: (set after login)
- `refresh_token`: (set after login)
- `emission_id`: (set after creating emissions)

## 🔥 Quick Start Testing Workflow

### Step 1: Health Check
```
GET http://localhost:8000/
```
**Expected Response:**
```json
{
  "message": "🌱 CarbonTrack API is running!",
  "version": "1.0.0",
  "docs": "http://localhost:8000/docs"
}
```

### Step 2: View API Documentation
```
GET http://localhost:8000/docs
```
This opens the interactive Swagger UI where you can also test endpoints.

## 🔐 Authentication Flow

### 1. Register a New User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "SecurePassword123!",
  "full_name": "Test User",
  "phone_number": "+1234567890"
}
```

**Expected Response:**
```json
{
  "message": "User registered successfully. Please check your email for verification.",
  "user_id": "user-uuid-here"
}
```

### 2. Login User
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "SecurePassword123!"
}
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "email": "test@example.com",
    "full_name": "Test User"
  }
}
```

**📝 Important:** Copy the `access_token` from the response and paste it into the Postman environment variable `access_token`.

### 3. Test Protected Endpoints
For all protected endpoints, include the Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

## 📊 Carbon Tracking Endpoints

### Add Carbon Emission
```http
POST /api/v1/carbon-emissions/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "date": "2024-01-15",
  "category": "transportation",
  "activity": "car_drive",
  "amount": 25.5,
  "unit": "km",
  "description": "Daily commute to office"
}
```

### Get All Emissions
```http
GET /api/v1/carbon-emissions/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Update Emission
```http
PUT /api/v1/carbon-emissions/{emission_id}
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "date": "2024-01-15",
  "category": "transportation",
  "activity": "car_drive",
  "amount": 30.0,
  "unit": "km",
  "description": "Updated daily commute distance"
}
```

### Delete Emission
```http
DELETE /api/v1/carbon-emissions/{emission_id}
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 📈 Analytics and Goals

### Get Analytics
```http
GET /api/v1/analytics/?start_date=2024-01-01&end_date=2024-12-31
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Create Goal
```http
POST /api/v1/goals/
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "title": "Reduce Transportation Emissions",
  "description": "Reduce car usage by 30% this year",
  "target_reduction": 30.0,
  "target_date": "2024-12-31",
  "category": "transportation"
}
```

### Get Goals
```http
GET /api/v1/goals/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Get Achievements
```http
GET /api/v1/achievements/
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 🔄 Token Management

### Refresh Access Token
```http
POST /api/v1/auth/refresh
Authorization: Bearer YOUR_REFRESH_TOKEN
```

### Reset Password
```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "email": "test@example.com"
}
```

### Confirm Password Reset
```http
POST /api/v1/auth/confirm-reset-password
Content-Type: application/json

{
  "email": "test@example.com",
  "confirmation_code": "123456",
  "new_password": "NewSecurePassword123!"
}
```

## 🧪 Testing Scenarios

### Scenario 1: Complete User Journey
1. ✅ Register new user
2. ✅ Login user (save tokens)
3. ✅ Add carbon emission
4. ✅ Get all emissions
5. ✅ Update emission
6. ✅ Get analytics
7. ✅ Create goal
8. ✅ Get achievements

### Scenario 2: Authentication Flow
1. ✅ Register user
2. ✅ Login user
3. ✅ Test protected endpoint with token
4. ✅ Refresh token
5. ✅ Test with new token

### Scenario 3: Error Handling
1. ❌ Try protected endpoint without token (401)
2. ❌ Try login with wrong credentials (401)
3. ❌ Try register with invalid email (422)
4. ❌ Try register with weak password (422)

## 📋 Expected Response Codes

| Endpoint | Method | Success Code | Description |
|----------|--------|--------------|-------------|
| `/` | GET | 200 | Health check |
| `/api/v1/auth/register` | POST | 201 | User registered |
| `/api/v1/auth/login` | POST | 200 | Login successful |
| `/api/v1/carbon-emissions/` | GET | 200 | Emissions retrieved |
| `/api/v1/carbon-emissions/` | POST | 201 | Emission created |
| `/api/v1/carbon-emissions/{id}` | PUT | 200 | Emission updated |
| `/api/v1/carbon-emissions/{id}` | DELETE | 204 | Emission deleted |
| `/api/v1/analytics/` | GET | 200 | Analytics retrieved |
| `/api/v1/goals/` | GET/POST | 200/201 | Goals operations |
| `/api/v1/achievements/` | GET | 200 | Achievements retrieved |

## 🚨 Common Error Responses

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## 🎯 Pro Tips for Testing

1. **Use Environment Variables**: Set up base_url, access_token, and refresh_token as environment variables in Postman
2. **Test Scripts**: Add Postman test scripts to automatically extract tokens from responses
3. **Collection Runner**: Use Postman's Collection Runner to run all tests automatically
4. **Data Management**: Use Postman's data files for testing with multiple users/scenarios
5. **Mock Responses**: Since we don't have real AWS Cognito setup, expect mock responses for authentication

## 🔧 Troubleshooting

### Server Not Running
```bash
cd /home/akabir/git/my-projects/CarbonTrack/backend
source ../.venv/bin/activate
uvicorn main:app --reload
```

### Invalid Token Error
- Check if token is correctly copied
- Verify token format: "Bearer <token>"
- Try refreshing the token

### CORS Issues
- CORS is configured for frontend development
- All origins are allowed in development mode

## 📚 Additional Resources

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

Happy testing! 🎉
