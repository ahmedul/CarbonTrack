# CarbonTrack Organization API Documentation

## Overview
This document describes the B2B multi-tenant organization APIs for CarbonTrack, enabling team carbon tracking, department management, and organization-wide analytics.

## Base URL
```
Production: https://nlkyarlri3.execute-api.eu-central-1.amazonaws.com/prod
Local: http://localhost:8000
```

## Authentication
All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

---

## Organization Management

### Create Organization
Create a new organization. The creating user becomes the organization admin.

**Endpoint:** `POST /api/v1/organizations`

**Request Body:**
```json
{
  "name": "Acme Corporation",
  "industry": "Technology",
  "size": "large",
  "subscription_tier": "enterprise"
}
```

**Fields:**
- `name` (string, required): Organization name
- `industry` (string, optional): Industry category. Default: "Other"
- `size` (string, optional): Organization size: "small", "medium", "large". Default: "small"
- `subscription_tier` (string, optional): Subscription plan: "free", "professional", "enterprise". Default: "free"

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Organization created successfully",
  "data": {
    "organization_id": "org_550e8400-e29b-41d4-a716-446655440000",
    "name": "Acme Corporation",
    "industry": "Technology",
    "size": "large",
    "subscription_tier": "enterprise",
    "admin_user_id": "user_123",
    "settings": {
      "carbon_budget": 0,
      "reporting_frequency": "monthly",
      "features_enabled": ["basic_tracking"],
      "branding": {}
    },
    "billing": {
      "plan": "enterprise",
      "seats": 1,
      "renewal_date": "2024-01-15T10:30:00"
    },
    "metadata": {},
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "status": "active"
  }
}
```

---

### Get Organization
Retrieve organization details by ID.

**Endpoint:** `GET /api/v1/organizations/{organization_id}`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "organization_id": "org_550e8400...",
    "name": "Acme Corporation",
    "industry": "Technology",
    "size": "large",
    "subscription_tier": "enterprise",
    "admin_user_id": "user_123",
    "settings": {...},
    "billing": {...},
    "status": "active"
  }
}
```

**Error Responses:**
- `404 Not Found`: Organization not found
- `500 Internal Server Error`: Server error

---

### Update Organization
Update organization details. Only organization admin or system admin can update.

**Endpoint:** `PUT /api/v1/organizations/{organization_id}`

**Request Body:**
```json
{
  "name": "Acme Corp",
  "industry": "Technology",
  "size": "large",
  "subscription_tier": "enterprise",
  "settings": {
    "carbon_budget": 500000,
    "reporting_frequency": "monthly",
    "features_enabled": ["bulk_import", "challenges", "advanced_reports"],
    "branding": {
      "logo_url": "https://example.com/logo.png",
      "primary_color": "#0066CC"
    }
  },
  "billing": {
    "plan": "enterprise",
    "seats": 500,
    "renewal_date": "2024-12-31T23:59:59"
  }
}
```

**Note:** All fields are optional. Only provided fields will be updated.

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Organization updated successfully",
  "data": {
    // Updated organization object
  }
}
```

**Error Responses:**
- `403 Forbidden`: User is not organization admin
- `404 Not Found`: Organization not found

---

### Delete Organization
Delete (deactivate) an organization. Only organization admin or system admin can delete.

**Endpoint:** `DELETE /api/v1/organizations/{organization_id}`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Organization deleted successfully"
}
```

**Note:** This is a soft delete - sets status to "inactive" rather than physically deleting.

---

### Get Organization Statistics
Get aggregated statistics and dashboard data for an organization.

**Endpoint:** `GET /api/v1/organizations/{organization_id}/stats`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "organization_id": "org_550e8400...",
    "total_teams": 5,
    "total_members": 250,
    "total_emissions": 125430.75,
    "average_per_member": 501.72,
    "active_goals": 3,
    "active_challenges": 1,
    "teams_breakdown": [
      {
        "team_id": "team_123",
        "name": "Engineering",
        "member_count": 120,
        "total_emissions": 45230.5,
        "average_per_member": 376.92
      },
      {
        "team_id": "team_456",
        "name": "Sales",
        "member_count": 80,
        "total_emissions": 78450.2,
        "average_per_member": 980.63
      }
    ]
  }
}
```

---

### List User Organizations
List all organizations where the user is an admin.

**Endpoint:** `GET /api/v1/users/{user_id}/organizations`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "organization_id": "org_123",
      "name": "Acme Corp",
      "industry": "Technology",
      "size": "large",
      "subscription_tier": "enterprise",
      "status": "active"
    },
    {
      "organization_id": "org_456",
      "name": "Green Energy Inc",
      "industry": "Energy",
      "size": "medium",
      "subscription_tier": "professional",
      "status": "active"
    }
  ]
}
```

**Error Responses:**
- `403 Forbidden`: User can only access their own organizations (unless system admin)

---

## Team Management

### Create Team
Create a new team/department within an organization.

**Endpoint:** `POST /api/v1/organizations/{organization_id}/teams`

**Request Body:**
```json
{
  "name": "Engineering",
  "description": "Product development and infrastructure teams",
  "team_lead_user_id": "user_456",
  "parent_team_id": ""
}
```

**Fields:**
- `name` (string, required): Team name
- `description` (string, optional): Team description
- `team_lead_user_id` (string, required): User ID of team lead
- `parent_team_id` (string, optional): Parent team ID for hierarchical structure

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Team created successfully",
  "data": {
    "team_id": "team_650e8400...",
    "organization_id": "org_550e8400...",
    "name": "Engineering",
    "description": "Product development and infrastructure teams",
    "parent_team_id": "",
    "team_lead_user_id": "user_456",
    "settings": {
      "carbon_budget": 0,
      "goal_period": "quarterly",
      "visibility": "org_only"
    },
    "stats": {
      "member_count": 0,
      "total_emissions": 0,
      "average_per_member": 0,
      "last_calculated": "2024-01-15T10:30:00"
    },
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "status": "active"
  }
}
```

---

### Get Team
Retrieve team details by ID.

**Endpoint:** `GET /api/v1/teams/{team_id}`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": {
    "team_id": "team_650e8400...",
    "organization_id": "org_550e8400...",
    "name": "Engineering",
    "description": "Product development and infrastructure teams",
    "team_lead_user_id": "user_456",
    "settings": {...},
    "stats": {...},
    "status": "active"
  }
}
```

---

### List Organization Teams
List all teams in an organization.

**Endpoint:** `GET /api/v1/organizations/{organization_id}/teams`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "team_id": "team_123",
      "name": "Engineering",
      "member_count": 120,
      "total_emissions": 45230.5
    },
    {
      "team_id": "team_456",
      "name": "Sales & Marketing",
      "member_count": 80,
      "total_emissions": 78450.2
    }
  ]
}
```

---

### Update Team
Update team details.

**Endpoint:** `PUT /api/v1/teams/{team_id}`

**Request Body:**
```json
{
  "name": "Engineering & Product",
  "description": "Updated description",
  "team_lead_user_id": "user_789",
  "settings": {
    "carbon_budget": 150000,
    "goal_period": "quarterly",
    "visibility": "org_only"
  }
}
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Team updated successfully",
  "data": {
    // Updated team object
  }
}
```

---

### Delete Team
Delete (archive) a team.

**Endpoint:** `DELETE /api/v1/teams/{team_id}`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Team deleted successfully"
}
```

---

## Team Membership

### Add Team Member
Add a user to a team.

**Endpoint:** `POST /api/v1/teams/{team_id}/members`

**Request Body:**
```json
{
  "user_id": "user_789",
  "role": "member"
}
```

**Fields:**
- `user_id` (string, required): User ID to add
- `role` (string, optional): Role: "member", "team_lead", "manager". Default: "member"

**Response:** `201 Created`
```json
{
  "success": true,
  "message": "Member added to team successfully",
  "data": {
    "team_id": "team_123",
    "user_id": "user_789",
    "organization_id": "org_123",
    "role": "member",
    "permissions": ["view_reports", "add_emissions"],
    "joined_at": "2024-01-15T10:30:00",
    "invited_by": "user_456",
    "status": "active"
  }
}
```

---

### Remove Team Member
Remove a user from a team.

**Endpoint:** `DELETE /api/v1/teams/{team_id}/members/{user_id}`

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Member removed from team successfully"
}
```

---

### List Team Members
List all members of a team.

**Endpoint:** `GET /api/v1/teams/{team_id}/members`

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "team_id": "team_123",
      "user_id": "user_456",
      "role": "team_lead",
      "permissions": ["view_reports", "add_members", "set_goals", "add_emissions"],
      "joined_at": "2024-01-01T00:00:00",
      "status": "active"
    },
    {
      "team_id": "team_123",
      "user_id": "user_789",
      "role": "member",
      "permissions": ["view_reports", "add_emissions"],
      "joined_at": "2024-01-15T10:30:00",
      "status": "active"
    }
  ]
}
```

---

### List User Teams
List all teams a user belongs to.

**Endpoint:** `GET /api/v1/users/{user_id}/teams`

**Query Parameters:**
- `organization_id` (string, optional): Filter by organization

**Response:** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "team_id": "team_123",
      "organization_id": "org_456",
      "role": "member",
      "joined_at": "2024-01-01T00:00:00"
    },
    {
      "team_id": "team_789",
      "organization_id": "org_456",
      "role": "team_lead",
      "joined_at": "2024-01-05T08:00:00"
    }
  ]
}
```

---

## Roles and Permissions

### Role Hierarchy
1. **Member**: Basic access to view reports and add emissions
2. **Team Lead**: Can add members and set team goals
3. **Manager**: Can edit team settings
4. **Organization Admin**: Full access to organization and all teams

### Permissions by Role

| Permission | Member | Team Lead | Manager | Admin |
|------------|--------|-----------|---------|-------|
| view_reports | ✓ | ✓ | ✓ | ✓ |
| add_emissions | ✓ | ✓ | ✓ | ✓ |
| add_members |  | ✓ | ✓ | ✓ |
| set_goals |  | ✓ | ✓ | ✓ |
| edit_team |  |  | ✓ | ✓ |
| delete_team |  |  |  | ✓ |

---

## Error Responses

### Standard Error Format
```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Rate Limiting
Not currently implemented. Will be added in future releases.

---

## Versioning
API version: `v1`

Current version: `1.0.0`

All endpoints are prefixed with `/api/v1/` for forward compatibility.

---

## Next Steps
Upcoming features:
- Team goals and tracking endpoints
- Team challenges and competitions
- Bulk data import
- Advanced reporting and CSV export
- Organization dashboard with analytics
