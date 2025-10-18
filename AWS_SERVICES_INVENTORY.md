# CarbonTrack AWS Services Inventory
**Last Updated:** October 14, 2025

## 🌍 Region Distribution Summary

### ✅ EU-CENTRAL-1 (Frankfurt) - PRIMARY REGION
**Status:** Active and configured as default
**Services:**

#### DynamoDB Tables (5)
1. ✅ `carbontrack-users` - User authentication and profiles
2. ✅ `carbontrack-entries` - Carbon emission entries
3. ✅ `carbontrack-goals` - Team goals (Phase 2 B2B)
4. ✅ `carbontrack-achievements` - User achievements/gamification
5. ✅ `carbontrack-emission-factors` - Emission calculation factors

#### Lambda Functions (1)
1. ✅ `carbontrack-api` 
   - Runtime: Python 3.10
   - Last Modified: 2025-10-08
   - Function URL: Available

#### API Gateway (1)
1. ✅ `carbontrack-api` (REST API)
   - API ID: `nlkyarlri3`
   - Endpoint: `https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod`
   - Type: REST API
   - Status: Deployed

---

### ⚠️ US-EAST-1 (N. Virginia) - LEGACY/MIXED REGION
**Status:** Contains duplicate/old tables - NEEDS CLEANUP
**Services:**

#### DynamoDB Tables (4)
1. ⚠️ `carbontrack-users` - **DUPLICATE** (also in eu-central-1)
2. ⚠️ `carbontrack-entries` - **DUPLICATE** (also in eu-central-1)
3. ⚠️ `carbontrack-users-production` - Legacy production table
4. ⚠️ `carbontrack-emissions-production` - Legacy production table

#### Lambda Functions
- ❌ None found

#### API Gateway
- ❌ None found

---

## 🔧 Configuration Issues Identified

### Problem 1: Mixed Region Data
- **Issue:** DynamoDB tables exist in both regions with same names
- **Impact:** Confusion about which tables are active
- **Solution:** Delete US-EAST-1 duplicates, keep EU-CENTRAL-1 only

### Problem 2: Backend Configuration
- **Issue:** Some code may reference us-east-1 region
- **Files to check:**
  - `backend/combined_api_server.py`
  - `backend/scripts/seed_*.py`
  - `backend/config.py`

### Problem 3: Frontend API URL
- **Issue:** Frontend hardcoded to production API
- **Current:** `https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod`
- **Local Dev:** Should use `http://localhost:8000` for development

---

## ✅ Recommended Actions

### Immediate (Fix Local Development)
1. ✅ Update all backend code to use `eu-central-1` consistently
2. ✅ Add environment-based API URL switching in frontend
3. ✅ Start local backend server for development
4. ✅ Test local environment works properly

### Short-term (Cleanup)
1. 🔄 Delete duplicate tables in us-east-1
2. 🔄 Archive legacy production tables if needed
3. 🔄 Update all documentation to reference eu-central-1

### Medium-term (Production Hardening)
1. 📋 Setup proper environment variables
2. 📋 Configure CloudWatch logging
3. 📋 Setup API Gateway custom domain
4. 📋 Configure SSL certificate (ACM)
5. 📋 Setup Route53 DNS

---

## 📊 Resource Costs (Estimated)

### Current Monthly Cost (Frankfurt Region)
- **DynamoDB (5 tables):** ~$2-5/month (on-demand pricing)
- **Lambda (carbontrack-api):** ~$0-2/month (< 1M requests)
- **API Gateway:** ~$0-1/month (< 1M requests)
- **Data Transfer:** ~$1-2/month
- **Total Estimate:** $5-10/month (very low usage)

### Additional Costs if Scaling
- **Custom Domain:** $0.50/month
- **ACM Certificate:** FREE
- **Route53 Hosted Zone:** $0.50/month
- **CloudWatch Logs:** ~$1-3/month

---

## 🚀 Production Deployment Checklist

### Infrastructure
- [ ] Consolidate all services to eu-central-1
- [ ] Delete us-east-1 duplicate tables
- [ ] Setup custom domain name
- [ ] Configure SSL certificate (ACM)
- [ ] Setup Route53 DNS records

### Security
- [ ] Enable API Gateway API keys
- [ ] Configure Lambda environment variables
- [ ] Setup IAM roles properly
- [ ] Enable CloudWatch logging
- [ ] Setup monitoring and alarms

### Application
- [ ] Update frontend API URL to custom domain
- [ ] Configure CORS properly
- [ ] Setup proper error handling
- [ ] Enable API rate limiting
- [ ] Setup backup strategy for DynamoDB

### Testing
- [ ] Test all API endpoints
- [ ] Verify authentication works
- [ ] Test data isolation (user sees only their data)
- [ ] Load test API endpoints
- [ ] Test error scenarios

---

## 🔗 Current Endpoints

### Production API (EU-CENTRAL-1)
```
Base URL: https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod
```

### Key Endpoints
- `POST /api/register` - User registration
- `POST /api/login` - User authentication
- `GET /api/profile` - Get user profile
- `GET /api/entries` - Get user's carbon entries
- `POST /api/entries` - Create carbon entry
- `GET /api/recommendations` - Get personalized recommendations
- `GET /api/achievements` - Get user achievements

### Local Development
```
Base URL: http://localhost:8000
```

---

## 📝 Notes

1. **Default Region:** AWS CLI configured to use eu-central-1
2. **Lambda Function URL:** Not currently using Function URLs, using API Gateway instead
3. **Database:** All active tables are in eu-central-1
4. **Cognito:** Not currently using AWS Cognito (using custom JWT auth)

---

## 🎯 Next Steps

1. **Fix Local Development** (TODAY)
   - Update backend region references
   - Start local server
   - Fix frontend API switching
   - Test full flow

2. **Cleanup AWS** (THIS WEEK)
   - Delete us-east-1 duplicates
   - Document cleanup
   - Verify production still works

3. **Production Polish** (NEXT WEEK)
   - Custom domain setup
   - SSL certificate
   - Professional deployment
   - Ready for funding demos

4. **Funding Preparation** (ONGOING)
   - Polish product
   - Create demo video
   - Prepare pitch deck
   - Research grant opportunities
