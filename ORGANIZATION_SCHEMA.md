# Multi-Tenant Organization Schema for CarbonTrack

## Overview
This document defines the database schema for B2B multi-user team carbon tracking with organizations, departments, teams, challenges, and goals.

## DynamoDB Tables

### 1. Organizations Table (`carbontrack-organizations`)

```
Primary Key:
- organization_id (HASH)     # Partition key: "org_uuid"

Attributes:
- organization_id: string    # "org_550e8400-e29b-41d4-a716-446655440000"
- name: string              # "Acme Corporation"
- industry: string          # "Technology", "Manufacturing", etc.
- size: string              # "small" (1-50), "medium" (51-500), "large" (500+)
- subscription_tier: string # "free", "professional", "enterprise"
- admin_user_id: string     # Primary admin user
- settings: map {
    carbon_budget: number      # Organization-wide carbon budget (kg CO2/year)
    reporting_frequency: string # "weekly", "monthly", "quarterly"
    features_enabled: list     # ["bulk_import", "challenges", "advanced_reports"]
    branding: map {
        logo_url: string
        primary_color: string
        custom_domain: string
    }
}
- billing: map {
    plan: string
    seats: number
    renewal_date: string
}
- metadata: map             # Custom fields, integrations
- created_at: string        # ISO timestamp
- updated_at: string        # ISO timestamp
- status: string            # "active", "suspended", "trial"
```

**GSIs:**
```
AdminUserIndex:
- admin_user_id (HASH)
- created_at (RANGE)
# Query: Find all organizations where user is admin
```

---

### 2. Teams/Departments Table (`carbontrack-teams`)

```
Primary Key:
- team_id (HASH)            # Partition key: "team_uuid"

Attributes:
- team_id: string           # "team_650e8400-e29b-41d4-a716-446655440000"
- organization_id: string   # Foreign key to organization
- name: string              # "Engineering", "Sales", "Marketing"
- description: string       # Team purpose/description
- parent_team_id: string    # For hierarchical org structure (optional)
- team_lead_user_id: string # Team leader/manager
- settings: map {
    carbon_budget: number      # Team-specific budget
    goal_period: string        # "monthly", "quarterly", "yearly"
    visibility: string         # "public", "org_only", "private"
}
- stats: map {
    member_count: number
    total_emissions: number    # Cached for performance
    average_per_member: number
    last_calculated: string    # When stats were last updated
}
- created_at: string
- updated_at: string
- status: string            # "active", "archived"
```

**GSIs:**
```
OrganizationTeamsIndex:
- organization_id (HASH)
- name (RANGE)
# Query: List all teams in an organization

TeamLeadIndex:
- team_lead_user_id (HASH)
- created_at (RANGE)
# Query: Teams where user is a team lead
```

---

### 3. Team Memberships Table (`carbontrack-team-members`)

```
Primary Key:
- team_id (HASH)            # Partition key
- user_id (RANGE)           # Sort key

Attributes:
- team_id: string
- user_id: string
- organization_id: string   # Denormalized for querying
- role: string              # "member", "team_lead", "manager"
- permissions: list         # ["view_reports", "add_members", "set_goals"]
- joined_at: string
- invited_by: string        # User ID who invited
- status: string            # "active", "invited", "inactive"
```

**GSIs:**
```
UserTeamsIndex:
- user_id (HASH)
- organization_id (RANGE)
# Query: All teams a user belongs to

OrganizationMembersIndex:
- organization_id (HASH)
- joined_at (RANGE)
# Query: All members across all teams in org
```

---

### 4. Team Goals Table (`carbontrack-team-goals`)

```
Primary Key:
- goal_id (HASH)            # Partition key: "goal_uuid"

Attributes:
- goal_id: string
- team_id: string
- organization_id: string   # Denormalized
- goal_type: string         # "reduction", "absolute", "per_capita"
- target_value: number      # Target emissions (kg CO2)
- baseline_value: number    # Starting point
- period: string            # "monthly", "quarterly", "yearly"
- start_date: string
- end_date: string
- status: string            # "active", "achieved", "failed", "cancelled"
- progress: map {
    current_value: number
    percentage: number
    last_updated: string
    on_track: boolean
}
- created_by: string        # User ID
- created_at: string
- updated_at: string
```

**GSIs:**
```
TeamGoalsIndex:
- team_id (HASH)
- start_date (RANGE)
# Query: All goals for a team

OrganizationGoalsIndex:
- organization_id (HASH)
- end_date (RANGE)
# Query: All goals in org, sorted by deadline
```

---

### 5. Challenges Table (`carbontrack-challenges`)

```
Primary Key:
- challenge_id (HASH)       # Partition key: "challenge_uuid"

Attributes:
- challenge_id: string
- organization_id: string   # Optional: org-only or public
- name: string              # "Q4 Emission Reduction Challenge"
- description: string
- challenge_type: string    # "reduction_race", "absolute_lowest", "improvement"
- rules: map {
    measurement: string        # "total", "per_capita", "percentage_reduction"
    duration_days: number
    min_participants: number
    categories: list          # ["transportation", "energy"] or "all"
}
- prizes: list [
    {rank: number, description: string, value: string}
]
- start_date: string
- end_date: string
- status: string            # "upcoming", "active", "completed", "cancelled"
- created_by: string        # User or org admin
- created_at: string
```

**GSIs:**
```
OrganizationChallengesIndex:
- organization_id (HASH)
- start_date (RANGE)
# Query: Challenges for an organization

StatusIndex:
- status (HASH)
- start_date (RANGE)
# Query: All active challenges globally
```

---

### 6. Challenge Participants Table (`carbontrack-challenge-participants`)

```
Primary Key:
- challenge_id (HASH)       # Partition key
- participant_id (RANGE)    # Sort key: "team_xxx" or "user_xxx"

Attributes:
- challenge_id: string
- participant_id: string    # Team ID or User ID
- participant_type: string  # "team", "individual"
- team_id: string          # If team participant
- organization_id: string
- stats: map {
    baseline_emissions: number    # Emissions before challenge
    current_emissions: number
    reduction_amount: number
    reduction_percentage: number
    rank: number
    last_updated: string
}
- joined_at: string
- status: string            # "active", "completed", "withdrawn"
```

**GSIs:**
```
ParticipantChallengesIndex:
- participant_id (HASH)
- joined_at (RANGE)
# Query: All challenges a team/user is in

OrganizationParticipantsIndex:
- organization_id (HASH)
- challenge_id (RANGE)
# Query: All participants from an org in various challenges
```

---

### 7. Updated Users Table (Add organization fields)

**Add to existing `carbontrack-users` table:**

```
Additional Attributes:
- organization_id: string        # Which org they belong to
- organization_role: string      # "member", "manager", "admin", "owner"
- teams: list [string]          # List of team IDs (denormalized for quick access)
- department: string            # Primary department/team name
- employee_id: string           # Company employee ID (optional)
- org_joined_at: string         # When joined organization
```

---

### 8. Updated Emissions Table (Add team tracking)

**Add to existing `carbontrack-entries` table:**

```
Additional Attributes:
- organization_id: string        # Which organization
- team_id: string               # Which team/department
- challenge_id: string          # If part of a challenge (optional)
- approved_by: string           # For bulk import validation
- import_batch_id: string       # For bulk import tracking
```

**Additional GSI:**
```
TeamEmissionsIndex:
- team_id (HASH)
- date (RANGE)
# Query: All emissions for a team by date

ChallengeEmissionsIndex:
- challenge_id (HASH)
- date (RANGE)
# Query: Emissions during a challenge period
```

---

## Data Access Patterns

### Organization Management
1. Create organization → Insert into Organizations table
2. Get organization details → Query by organization_id
3. List user's organizations → Query AdminUserIndex
4. Update organization settings → Update item by organization_id

### Team Management
5. Create team → Insert into Teams table
6. List organization teams → Query OrganizationTeamsIndex
7. Get team details → Query by team_id
8. Add member to team → Insert into TeamMemberships
9. List user's teams → Query UserTeamsIndex
10. List team members → Query by team_id on TeamMemberships

### Dashboard & Analytics
11. Organization dashboard → Query OrganizationTeamsIndex + aggregate team stats
12. Team dashboard → Query TeamEmissionsIndex + aggregate
13. Department comparison → Query multiple teams via OrganizationTeamsIndex
14. Individual leaderboard → Query UserTeamsIndex + emissions data

### Goals & Tracking
15. Set team goal → Insert into TeamGoals
16. Track goal progress → Query TeamGoalsIndex + calculate from emissions
17. List active goals → Query OrganizationGoalsIndex with status filter

### Challenges
18. Create challenge → Insert into Challenges table
19. Join challenge → Insert into ChallengeParticipants
20. Get challenge leaderboard → Query ChallengeParticipants + sort by stats.rank
21. List active challenges → Query StatusIndex where status="active"

---

## Indexes Summary

**Required GSIs:**
1. Organizations: AdminUserIndex
2. Teams: OrganizationTeamsIndex, TeamLeadIndex
3. TeamMemberships: UserTeamsIndex, OrganizationMembersIndex
4. TeamGoals: TeamGoalsIndex, OrganizationGoalsIndex
5. Challenges: OrganizationChallengesIndex, StatusIndex
6. ChallengeParticipants: ParticipantChallengesIndex, OrganizationParticipantsIndex
7. Emissions: TeamEmissionsIndex, ChallengeEmissionsIndex (new)

---

## Implementation Priority

**Phase 1 - Foundation:**
- Organizations table
- Teams table
- Team memberships table
- Basic CRUD APIs

**Phase 2 - Analytics:**
- Organization dashboard
- Team statistics
- Department comparisons

**Phase 3 - Engagement:**
- Team goals
- Progress tracking
- Leaderboards

**Phase 4 - Gamification:**
- Challenges system
- Competition leaderboards
- Prizes/rewards

**Phase 5 - Enterprise:**
- Bulk data import
- Advanced reporting
- Custom integrations

---

## Permissions Model

```
Organization Owner: Full access to everything
Organization Admin: Manage teams, users, view all data, set org goals
Team Manager: Manage team members, set team goals, view team data
Team Lead: View team data, add emissions, limited member management
Member: View own data, add own emissions, participate in challenges
```

---

## Cost Optimization Notes

1. **Denormalization**: Store organization_id in team/membership tables to avoid joins
2. **Caching**: Cache team stats in Teams table, update periodically
3. **Batch operations**: Use BatchGetItem for dashboard queries
4. **Pagination**: Implement for large team/org listings
5. **Conditional writes**: Use for concurrent updates to prevent race conditions
