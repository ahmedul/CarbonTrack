# Admin Visibility & Analytics Features

## Overview
As an admin, you have comprehensive visibility into all system data including CSRD reports, carbon entries, user activity, and revenue metrics.

## Admin Endpoints Available

### 1. User Management
**GET /api/v1/admin/users**
- View all users across all tiers
- See user status (active/pending/inactive)
- Access user details and activity

**GET /api/v1/admin/pending-users**
- View users awaiting approval
- Quick access to pending registrations

**POST /api/v1/admin/users/{user_id}/approve**
- Approve pending users
- Grant system access

**DELETE /api/v1/admin/users/{user_id}**
- Remove users from system
- Cascade delete their data

---

### 2. CSRD Reports Visibility
**GET /api/v1/admin/csrd/reports/all**

View ALL CSRD reports across ALL companies:

```bash
curl "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/admin/csrd/reports/all" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Response includes:**
```json
{
  "success": true,
  "total_reports": 45,
  "unique_companies": 12,
  "companies": ["Acme Corp", "Tech GmbH", "Green Industries", ...],
  "total_emissions_tco2e": 125450.5,
  "reports": [
    {
      "report_id": "csrd_2025_abc123",
      "company_name": "Acme Corporation",
      "company_id": "comp_123",
      "user_id": "user_456",
      "reporting_year": 2025,
      "status": "IN_PROGRESS",
      "completeness_score": 67.5,
      "total_emissions_tco2e": 15234.75,
      "employee_count": 350,
      "revenue_eur": 75000000,
      "country": "DE",
      "created_at": "2025-11-15T10:30:00Z",
      "updated_at": "2025-12-10T14:20:00Z"
    },
    ...
  ]
}
```

**What you can see:**
- ✅ Which companies are generating CSRD reports
- ✅ Report completion status (NOT_STARTED, IN_PROGRESS, IN_REVIEW, COMPLETED, SUBMITTED)
- ✅ Total emissions per company (Scope 1+2+3)
- ✅ Company size (employees, revenue)
- ✅ Geographic distribution (country codes)
- ✅ Timeline (when created, last updated)

**Filter options:**
```bash
# Filter by status
GET /api/v1/admin/csrd/reports/all?status_filter=COMPLETED

# Limit results
GET /api/v1/admin/csrd/reports/all?limit=50
```

---

### 3. Companies Using CSRD
**GET /api/v1/admin/companies/csrd-users**

Get detailed list of companies using the CSRD module:

```json
{
  "success": true,
  "total_companies": 12,
  "companies": [
    {
      "company_name": "Acme Corporation",
      "company_id": "comp_123",
      "user_ids": ["user_456", "user_789"],  // Multiple users per company
      "total_reports": 3,
      "years_covered": [2023, 2024, 2025],
      "reports": [
        {
          "year": 2025,
          "status": "IN_PROGRESS",
          "created_at": "2025-11-15T10:30:00Z"
        },
        {
          "year": 2024,
          "status": "SUBMITTED",
          "created_at": "2024-12-01T09:15:00Z"
        }
      ]
    },
    ...
  ]
}
```

**Insights:**
- ✅ All companies using CSRD module
- ✅ Historical reports per company
- ✅ Multi-year tracking
- ✅ Active vs completed reports
- ✅ User associations

---

### 4. Carbon Entries (All Users)
**GET /api/v1/admin/carbon/entries/all**

View ALL carbon footprint entries from ALL users:

```json
{
  "success": true,
  "total_entries": 2847,
  "unique_users": 156,
  "total_co2_kg": 45678.25,
  "total_co2_tonnes": 45.67,
  "categories": {
    "transportation": {
      "count": 892,
      "total_co2_kg": 23450.5
    },
    "energy": {
      "count": 654,
      "total_co2_kg": 15200.75
    },
    "food": {
      "count": 1301,
      "total_co2_kg": 7027.0
    }
  },
  "entries": [
    {
      "entry_id": "entry_123",
      "user_id": "user_456",
      "category": "transportation",
      "date": "2025-12-10",
      "activity_type": "car",
      "description": "Commute to work",
      "co2_kg": 12.5,
      "amount": 50,
      "created_at": "2025-12-10T08:30:00Z"
    },
    ...
  ]
}
```

**Analytics capabilities:**
- ✅ System-wide carbon tracking
- ✅ Breakdown by category
- ✅ User activity patterns
- ✅ Total environmental impact
- ✅ Individual entry details

---

### 5. Comprehensive Dashboard
**GET /api/v1/admin/dashboard/comprehensive**

Get complete system overview in one call:

```json
{
  "success": true,
  "users": {
    "total_users": 245,
    "by_tier": {
      "FREE": 150,
      "BASIC": 45,
      "PROFESSIONAL": 35,
      "BUSINESS": 15
    },
    "csrd_access_count": 50
  },
  "csrd": {
    "total_reports": 45,
    "by_status": {
      "NOT_STARTED": 8,
      "IN_PROGRESS": 22,
      "IN_REVIEW": 7,
      "COMPLETED": 6,
      "SUBMITTED": 2
    },
    "total_emissions_tco2e": 125450.5,
    "unique_companies": 12
  },
  "carbon": {
    "total_entries": 2847,
    "total_co2_kg": 45678.25,
    "by_category": {
      "transportation": 23450.5,
      "energy": 15200.75,
      "food": 7027.0
    }
  },
  "revenue": {
    "monthly_eur": 14355,
    "annual_eur": 172260
  },
  "timestamp": "2025-12-12T22:30:00Z"
}
```

**Business insights:**
- ✅ User distribution across pricing tiers
- ✅ CSRD adoption rate (50 users = 20%)
- ✅ Revenue tracking (MRR/ARR)
- ✅ System activity metrics
- ✅ Environmental impact totals

---

### 6. Legacy Stats Endpoint
**GET /api/v1/admin/stats**

Simplified stats for backward compatibility:

```json
{
  "success": true,
  "stats": {
    "total_users": 245,
    "pending_registrations": 12,
    "active_this_month": 1847,
    "total_carbon_tracked": 45678.25,
    "total_entries": 2847
  }
}
```

---

## Access Control

### Who Can Access Admin Endpoints?

1. **Admin Role**: Users with `role: "admin"` in DynamoDB
2. **Admin Email**: `ahmedulkabir55@gmail.com` (hardcoded admin)
3. **Demo Users**: Users with IDs starting with `demo-`, `mock_`, or `test_` (for testing)

### Authentication Required

All admin endpoints require:
```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

Get your token from:
- Login: `POST /api/login`
- Your Cognito session

---

## Example Admin Workflow

### 1. Check System Health
```bash
curl "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/admin/dashboard/comprehensive" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. See Which Companies Use CSRD
```bash
curl "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/admin/companies/csrd-users" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. View All CSRD Reports
```bash
curl "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/admin/csrd/reports/all" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Check Carbon Activity
```bash
curl "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/admin/carbon/entries/all?limit=200" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 5. Monitor Revenue
```bash
curl "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/admin/dashboard/comprehensive" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq '.revenue'
```

---

## Key Metrics You Can Track

### CSRD Module Adoption
- **Total CSRD reports**: How many companies are using the feature
- **Completion rate**: % of reports submitted vs in-progress
- **Average emissions**: tCO2e per company
- **Geographic spread**: Which countries are most active
- **Year-over-year**: Historical reporting trends

### Carbon Tracking Usage
- **Total entries**: Overall system activity
- **Unique users**: Active user count
- **Category breakdown**: What people track most (transportation, energy, food)
- **Total impact**: Cumulative CO2 tracked across all users

### Business Metrics
- **User distribution**: FREE vs paid tiers
- **CSRD penetration**: % of users with CSRD access
- **Revenue**: MRR and ARR from subscriptions
- **Growth**: New signups vs churn

### Compliance & Quality
- **Report status**: How many reports are completed
- **Data completeness**: Average completeness scores
- **Verification rate**: % of reports verified
- **Audit activity**: Change tracking

---

## Security Notes

⚠️ **Admin endpoints expose sensitive data**
- Only authenticated admins can access
- Returns data across ALL users and companies
- Includes PII (emails, company names)
- Should be logged and monitored

✅ **Best practices:**
- Use admin endpoints sparingly
- Log all admin access
- Rotate admin credentials regularly
- Monitor for unauthorized access
- Consider IP whitelisting for admin API

---

## Next Steps

### Deployment
The admin endpoints are already included in:
- `backend/deployment-full/app/api/v1/admin.py`
- Registered in `backend/deployment-full/main.py`

To deploy:
```bash
cd /home/akabir/git/my-projects/CarbonTrack/backend
./deploy-with-csrd-layer.sh
```

### Testing
```bash
# Get your admin JWT token
TOKEN="YOUR_ADMIN_TOKEN_HERE"

# Test CSRD visibility
curl "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/admin/csrd/reports/all" \
  -H "Authorization: Bearer $TOKEN"

# Test comprehensive dashboard
curl "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/admin/dashboard/comprehensive" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Summary

**Yes, as admin you can see:**
- ✅ **All CSRD reports** from all companies
- ✅ **All carbon entries** from all users
- ✅ **Which companies** are generating CSRD reports
- ✅ **User analytics** by tier and subscription
- ✅ **Revenue metrics** (MRR, ARR)
- ✅ **System health** and activity trends
- ✅ **Compliance status** across all reports
- ✅ **Environmental impact** totals

**The admin API provides complete system visibility!** 🎉
