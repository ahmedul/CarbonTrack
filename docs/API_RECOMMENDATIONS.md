# Recommendation System API Documentation

## Overview

The CarbonTrack Recommendation API provides intelligent, personalized carbon reduction suggestions based on user behavior analysis and scientific emission data.

## Authentication

All recommendation endpoints require authentication via JWT Bearer token:

```http
Authorization: Bearer <jwt_token>
```

## Base URL

```
https://api.carbontrack.com/v1/recommendations
```

## Endpoints

### 1. Get Personalized Recommendations

**GET** `/`

Retrieve personalized carbon reduction recommendations for the authenticated user.

#### Query Parameters

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `category` | string | No | Filter by category (transportation, energy, food, waste, lifestyle) | All categories |
| `limit` | integer | No | Maximum number of recommendations (1-50) | 10 |

#### Request Example

```http
GET /api/v1/recommendations/?category=transportation&limit=5
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response Schema

```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "id": "switch_to_hybrid",
        "title": "Switch to Hybrid Vehicle",
        "description": "Hybrid vehicles can reduce transportation emissions by 25-45%",
        "category": "transportation",
        "difficulty": "Medium",
        "cost": "Medium Cost",
        "timeframe": "medium-term",
        "co2_savings_kg": 1245.5,
        "score": 87,
        "action_steps": [
          "Research hybrid models in your price range",
          "Calculate fuel savings and tax incentives",
          "Visit dealers for test drives",
          "Consider certified pre-owned options"
        ],
        "estimated_implementation_cost": "$15,000 - $35,000",
        "payback_period_months": 36,
        "environmental_impact": "High",
        "user_relevance_factors": [
          "Daily commute: 30km",
          "Current vehicle: Medium gasoline car",
          "High transportation emissions"
        ]
      }
    ],
    "user_patterns": {
      "total_emissions": 2847.3,
      "category_breakdown": {
        "transportation": 1138.9,
        "energy": 996.4,
        "food": 568.7,
        "waste": 143.3
      },
      "top_activities": [
        ["Medium Gasoline Car", 1138.9],
        ["Electricity Usage", 856.2],
        ["Natural Gas", 140.2]
      ],
      "patterns": {
        "dominant_category": {
          "category": "transportation",
          "percentage": 40.0
        },
        "distribution": "concentrated"
      }
    },
    "total_potential_savings_kg": 3421.8,
    "implementation_stats": {
      "easy": 3,
      "medium": 1,
      "hard": 1,
      "free": 2,
      "low_cost": 2,
      "medium_cost": 1
    },
    "count": 5
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique recommendation identifier |
| `title` | string | Human-readable recommendation title |
| `description` | string | Detailed explanation of the recommendation |
| `category` | string | Emission category (transportation, energy, food, waste, lifestyle) |
| `difficulty` | string | Implementation difficulty (Easy, Medium, Hard) |
| `cost` | string | Implementation cost (Free, Low Cost, Medium Cost, High Cost) |
| `timeframe` | string | Implementation timeframe (immediate, short-term, medium-term, long-term) |
| `co2_savings_kg` | number | Estimated annual CO₂ savings in kilograms |
| `score` | integer | Relevance score (0-100) based on user patterns |
| `action_steps` | array | Specific steps to implement the recommendation |
| `estimated_implementation_cost` | string | Cost range for implementation |
| `payback_period_months` | integer | Time to recover investment through savings |
| `environmental_impact` | string | Impact level (Low, Medium, High) |
| `user_relevance_factors` | array | Why this recommendation is relevant to the user |

### 2. Get Recommendation Categories

**GET** `/categories`

Retrieve available recommendation categories with descriptions.

#### Request Example

```http
GET /api/v1/recommendations/categories
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response Example

```json
{
  "success": true,
  "data": {
    "categories": {
      "transportation": {
        "name": "Transportation",
        "description": "Reduce emissions from travel and commuting",
        "icon": "🚗",
        "typical_savings_range": "10-90%",
        "common_actions": ["Vehicle efficiency", "Alternative transport", "Trip optimization"]
      },
      "energy": {
        "name": "Energy",
        "description": "Optimize home and office energy usage",
        "icon": "⚡",
        "typical_savings_range": "15-85%",
        "common_actions": ["Renewable energy", "Efficiency improvements", "Smart usage"]
      },
      "food": {
        "name": "Food & Diet",
        "description": "Make sustainable dietary choices",
        "icon": "🥗",
        "typical_savings_range": "20-75%",
        "common_actions": ["Plant-rich diet", "Local sourcing", "Waste reduction"]
      },
      "waste": {
        "name": "Waste Management",
        "description": "Reduce, reuse, and recycle effectively",
        "icon": "♻️",
        "typical_savings_range": "40-80%",
        "common_actions": ["Recycling", "Composting", "Waste reduction"]
      },
      "lifestyle": {
        "name": "Lifestyle",
        "description": "Adopt sustainable living practices",
        "icon": "🌱",
        "typical_savings_range": "5-50%",
        "common_actions": ["Conscious consumption", "Digital efficiency", "Sustainable choices"]
      }
    }
  }
}
```

### 3. Get Recommendation Statistics

**GET** `/stats`

Retrieve comprehensive statistics about recommendations and potential impact.

#### Request Example

```http
GET /api/v1/recommendations/stats
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Response Example

```json
{
  "success": true,
  "data": {
    "total_recommendations": 23,
    "by_category": {
      "transportation": 8,
      "energy": 6,
      "food": 5,
      "waste": 3,
      "lifestyle": 1
    },
    "by_difficulty": {
      "Easy": 12,
      "Medium": 8,
      "Hard": 3
    },
    "by_cost": {
      "Free": 8,
      "Low Cost": 7,
      "Medium Cost": 5,
      "High Cost": 3
    },
    "potential_impact": {
      "total_co2_savings_kg": 4567.8,
      "high_impact_count": 6,
      "quick_wins": 8,
      "average_savings_per_recommendation": 198.6
    },
    "user_specific_metrics": {
      "most_relevant_category": "transportation",
      "easiest_high_impact_actions": 3,
      "potential_monthly_savings": 380.7,
      "implementation_feasibility_score": 0.74
    }
  }
}
```

## Error Responses

### Standard Error Format

```json
{
  "success": false,
  "error": {
    "code": "INVALID_CATEGORY",
    "message": "Invalid category specified. Must be one of: transportation, energy, food, waste, lifestyle",
    "details": {
      "provided_category": "invalid_category",
      "valid_categories": ["transportation", "energy", "food", "waste", "lifestyle"]
    }
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing authentication token |
| `INVALID_CATEGORY` | 400 | Invalid category filter provided |
| `INVALID_LIMIT` | 400 | Limit parameter out of range (1-50) |
| `USER_NOT_FOUND` | 404 | User profile not found |
| `INSUFFICIENT_DATA` | 422 | Not enough user activity data for personalization |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests in time window |
| `INTERNAL_ERROR` | 500 | Server error during recommendation generation |

## Rate Limiting

- **Rate Limit**: 100 requests per hour per user
- **Burst Limit**: 10 requests per minute
- **Headers**: Rate limit information included in response headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Data Freshness

- **User Pattern Analysis**: Updated in real-time when new activities are added
- **Recommendation Scores**: Recalculated when user patterns change significantly
- **Scientific Data**: Emission factors updated quarterly from authoritative sources
- **Recommendation Database**: New recommendations added monthly

## Webhook Integration

### Recommendation Updates

Subscribe to webhook notifications when new recommendations become available:

```json
{
  "event": "recommendations.updated",
  "user_id": "user_123",
  "data": {
    "new_recommendations_count": 3,
    "updated_at": "2025-09-30T14:30:00Z",
    "trigger_reason": "new_activity_added",
    "categories_affected": ["transportation", "energy"]
  }
}
```

## SDK and Client Libraries

### JavaScript/Node.js

```javascript
import { CarbonTrackClient } from '@carbontrack/js-sdk';

const client = new CarbonTrackClient({
  apiKey: 'your-api-key',
  baseURL: 'https://api.carbontrack.com/v1'
});

// Get recommendations
const recommendations = await client.recommendations.list({
  category: 'transportation',
  limit: 10
});

// Get statistics
const stats = await client.recommendations.getStats();
```

### Python

```python
from carbontrack import CarbonTrackClient

client = CarbonTrackClient(api_key='your-api-key')

# Get recommendations
recommendations = client.recommendations.list(
    category='transportation',
    limit=10
)

# Get categories
categories = client.recommendations.get_categories()
```

## Best Practices

### Caching Recommendations

- Cache recommendations for 1-4 hours depending on user activity frequency
- Invalidate cache when new activities are added
- Use ETags for conditional requests

### Pagination

For users with many recommendations, implement pagination:

```http
GET /api/v1/recommendations/?page=2&limit=10
```

### Progressive Enhancement

1. **Initial Load**: Show general recommendations immediately
2. **Personalization**: Load personalized recommendations asynchronously
3. **Real-time Updates**: Use WebSockets for live recommendation updates

### Error Handling

```javascript
try {
  const recommendations = await client.recommendations.list();
} catch (error) {
  if (error.code === 'INSUFFICIENT_DATA') {
    // Show onboarding flow to gather more user data
    showOnboarding();
  } else if (error.code === 'RATE_LIMIT_EXCEEDED') {
    // Implement exponential backoff
    await delay(60000);
    retry();
  }
}
```

## Performance Metrics

### API Performance SLAs

- **Response Time**: 95th percentile < 200ms
- **Availability**: 99.9% uptime
- **Data Accuracy**: Emission calculations within 5% of scientific standards
- **Personalization Quality**: >80% user relevance score

### Monitoring

Key metrics to monitor:

- Recommendation click-through rates
- Implementation success rates
- User satisfaction scores
- CO₂ savings achieved vs. predicted