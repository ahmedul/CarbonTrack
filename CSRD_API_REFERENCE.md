# CSRD API Quick Reference

**Base URL:** `https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod`  
**Authentication:** Bearer token required for all endpoints  
**Subscription Required:** PROFESSIONAL, BUSINESS, or ENTERPRISE tier

## 🔐 Authentication

```bash
# Login to get access token
curl -X POST "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"your@email.com","password":"yourpassword"}'

# Response
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## 📋 CSRD Endpoints

### 1. List Reports
```bash
GET /api/v1/csrd/reports?status=draft&year=2024

curl -H "Authorization: Bearer TOKEN" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports"
```

**Query Parameters:**
- `status` (optional): draft, submitted, verified
- `year` (optional): Reporting year (default: current year)
- `standard` (optional): Filter by ESRS standard (E1, E2, etc.)

### 2. Create Report
```bash
POST /api/v1/csrd/reports

curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports" \
  -d '{
    "reporting_year": 2024,
    "reporting_period_start": "2024-01-01",
    "reporting_period_end": "2024-12-31",
    "standards": ["E1", "E2", "S1"],
    "status": "draft"
  }'
```

**Request Body:**
```json
{
  "reporting_year": 2024,
  "reporting_period_start": "2024-01-01",
  "reporting_period_end": "2024-12-31",
  "standards": ["E1", "E2", "E3", "E4", "E5", "S1", "G1"],
  "status": "draft"
}
```

### 3. Get Report Details
```bash
GET /api/v1/csrd/reports/{report_id}

curl -H "Authorization: Bearer TOKEN" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports/123"
```

### 4. Update Report
```bash
PUT /api/v1/csrd/reports/{report_id}

curl -X PUT -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports/123" \
  -d '{
    "metrics": {
      "E1": {
        "scope_1": 1500.5,
        "scope_2": 850.2,
        "scope_3": 3200.8,
        "renewable_energy": 45.5
      }
    }
  }'
```

**Metrics Structure:**
```json
{
  "metrics": {
    "E1": {
      "scope_1": 1500.5,
      "scope_2": 850.2,
      "scope_3": 3200.8,
      "renewable_energy": 45.5
    },
    "E2": {
      "air_emissions": 120.3,
      "water_pollutants": 45.2
    },
    "E3": {
      "water_consumption": 15000,
      "water_discharge": 12000
    }
  }
}
```

### 5. Submit Report
```bash
POST /api/v1/csrd/reports/{report_id}/submit

curl -X POST -H "Authorization: Bearer TOKEN" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports/123/submit"
```

**Effect:** Changes status from `draft` to `submitted`. Cannot be edited after submission.

### 6. Third-Party Verification
```bash
POST /api/v1/csrd/reports/{report_id}/verify

curl -X POST -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports/123/verify" \
  -d '{
    "verifier_name": "Green Audit Corp",
    "verification_date": "2024-03-15",
    "certificate_number": "CERT-2024-001",
    "assurance_level": "limited"
  }'
```

**Verification Levels:**
- `limited` - Limited assurance verification
- `reasonable` - Reasonable assurance verification

### 7. Get Audit Trail
```bash
GET /api/v1/csrd/reports/{report_id}/audit-trail

curl -H "Authorization: Bearer TOKEN" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports/123/audit-trail"
```

**Response:**
```json
[
  {
    "timestamp": "2024-11-30T10:15:30Z",
    "action": "created",
    "user": "user@company.com",
    "changes": {
      "status": "draft"
    }
  },
  {
    "timestamp": "2024-11-30T14:20:45Z",
    "action": "updated",
    "user": "user@company.com",
    "changes": {
      "metrics.E1.scope_1": [1200.5, 1500.5]
    }
  }
]
```

### 8. Export as PDF
```bash
GET /api/v1/csrd/reports/{report_id}/export/pdf

curl -H "Authorization: Bearer TOKEN" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports/123/export/pdf"
```

**Response:**
```json
{
  "download_url": "https://s3.eu-central-1.amazonaws.com/...",
  "expires_in": 3600
}
```

### 9. List ESRS Standards
```bash
GET /api/v1/csrd/standards

curl -H "Authorization: Bearer TOKEN" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/standards"
```

**Response:**
```json
[
  {
    "code": "E1",
    "name": "Climate Change",
    "description": "GHG emissions, energy, climate adaptation",
    "required_metrics": ["scope_1", "scope_2", "scope_3", "renewable_energy"],
    "esrs_standard": "E1_CLIMATE"
  },
  {
    "code": "E2",
    "name": "Pollution",
    "description": "Air, water, soil pollution management",
    "required_metrics": ["air_emissions", "water_pollutants", "soil_contamination"],
    "esrs_standard": "E2_POLLUTION"
  }
]
```

### 10. Check Compliance
```bash
GET /api/v1/csrd/compliance-check/{report_id}

curl -H "Authorization: Bearer TOKEN" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/compliance-check/123"
```

**Response:**
```json
{
  "report_id": "123",
  "completeness_score": 75.5,
  "is_compliant": false,
  "missing_data": {
    "E1": ["scope_3"],
    "E3": ["water_discharge"]
  },
  "recommendations": [
    "Complete Scope 3 emissions data for E1",
    "Add water discharge metrics for E3"
  ]
}
```

### 11. Compliance Calendar
```bash
GET /api/v1/csrd/deadline-calendar?year=2026

curl -H "Authorization: Bearer TOKEN" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/deadline-calendar?year=2026"
```

**Response:**
```json
[
  {
    "date": "2026-01-31",
    "milestone": "Q4 data collection deadline",
    "description": "Complete data collection for Q4 of previous year",
    "priority": "high"
  },
  {
    "date": "2026-03-31",
    "milestone": "First draft completion",
    "description": "Complete first draft of all ESRS sections",
    "priority": "high"
  }
]
```

## 🎯 ESRS Standards Reference

| Code | Standard | Key Metrics |
|------|----------|-------------|
| **E1** | Climate Change | Scope 1, 2, 3 emissions, renewable energy % |
| **E2** | Pollution | Air emissions, water pollutants, soil contamination |
| **E3** | Water & Marine | Water consumption, discharge, marine impact |
| **E4** | Biodiversity | Land use, habitat protection, ecosystem impact |
| **E5** | Circular Economy | Waste generation, recycling rate, resource use |
| **S1** | Own Workforce | Employee metrics, diversity, training hours |
| **G1** | Business Conduct | Governance structure, ethics, anti-corruption |

## 🔒 Error Responses

### Premium Feature Required (402)
```json
{
  "detail": {
    "error": "Premium Feature Required",
    "message": "CSRD Compliance Module requires a PROFESSIONAL, BUSINESS, or ENTERPRISE subscription",
    "current_tier": "free",
    "required_tiers": ["PROFESSIONAL", "BUSINESS", "ENTERPRISE"],
    "upgrade_url": "/api/v1/subscriptions/upgrade"
  }
}
```

### Unauthorized (401)
```json
{
  "detail": "Not authenticated"
}
```

### Not Found (404)
```json
{
  "detail": "Report not found"
}
```

### Validation Error (422)
```json
{
  "detail": [
    {
      "loc": ["body", "reporting_year"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 💡 Common Use Cases

### Creating a Complete CSRD Report

```bash
# 1. Create draft report
REPORT=$(curl -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports" \
  -d '{
    "reporting_year": 2024,
    "reporting_period_start": "2024-01-01",
    "reporting_period_end": "2024-12-31",
    "standards": ["E1", "E2", "S1"]
  }')

REPORT_ID=$(echo $REPORT | jq -r '.report_id')

# 2. Add metrics
curl -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports/$REPORT_ID" \
  -d '{
    "metrics": {
      "E1": {
        "scope_1": 1500.5,
        "scope_2": 850.2,
        "scope_3": 3200.8,
        "renewable_energy": 45.5
      }
    }
  }'

# 3. Check compliance
curl -H "Authorization: Bearer $TOKEN" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/compliance-check/$REPORT_ID"

# 4. Submit report
curl -X POST -H "Authorization: Bearer $TOKEN" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports/$REPORT_ID/submit"

# 5. Export as PDF
curl -H "Authorization: Bearer $TOKEN" \
  "https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod/api/v1/csrd/reports/$REPORT_ID/export/pdf"
```

## 🚀 Next Steps

1. **Upgrade Subscription** - Required to use CSRD features
2. **Create Your First Report** - Start with draft status
3. **Add Metrics** - Fill in data for each ESRS standard
4. **Check Compliance** - Verify completeness before submission
5. **Submit** - Finalize your report
6. **Export** - Download PDF for stakeholders

---

**Documentation Version:** 1.0  
**Last Updated:** November 30, 2025  
**API Version:** 2.0.0
