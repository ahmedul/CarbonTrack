# CarbonTrack Database Schema Documentation

## DynamoDB Table Design

### 1. CarbonDataTable (carbon emissions data)

```
Primary Key:
- user_id (HASH)      # Partition key - distributes data
- timestamp (RANGE)   # Sort key - orders entries chronologically

Attributes:
- user_id: string           # "user_123"
- timestamp: string         # "2024-03-15T10:30:00Z"  
- activity_type: string     # "transportation", "energy", "food", "waste"
- category: string          # "car", "electricity", "beef", "plastic"
- amount: number            # 50 (miles driven, kWh used, etc.)
- unit: string              # "miles", "kwh", "lbs"
- co2_emissions: number     # 25.5 (kg CO2)
- organization_id: string   # "org_456" (for enterprise features)
- metadata: map             # Additional activity details
```

Global Secondary Indexes (GSIs):
```
OrganizationIndex:
- organization_id (HASH)    # Query by organization
- timestamp (RANGE)         # Order by date
```

### 2. UsersTable (user profiles and settings)

```
Primary Key:
- user_id (HASH)            # Partition key

Attributes:
- user_id: string           # "user_123"
- email: string             # "john@example.com"
- name: string              # "John Doe"
- organization_id: string   # "org_456"
- role: string              # "user", "admin", "org_admin"
- preferences: map          # Settings and preferences
- created_at: string        # Account creation date
- last_login: string        # Last activity timestamp
```

Global Secondary Indexes:
```
EmailIndex:
- email (HASH)              # Login by email

OrganizationIndex:
- organization_id (HASH)    # Query organization members
```

## Query Patterns

### Individual User Queries
```python
# Get user's recent emissions
table.query(
    KeyConditionExpression=Key('user_id').eq('user_123') & 
                          Key('timestamp').between('2024-01-01', '2024-12-31')
)

# Get specific activity types
table.query(
    KeyConditionExpression=Key('user_id').eq('user_123'),
    FilterExpression=Attr('activity_type').eq('transportation')
)
```

### Organization Queries (Enterprise Feature)
```python
# Get all organization emissions
table.query(
    IndexName='OrganizationIndex',
    KeyConditionExpression=Key('organization_id').eq('org_456')
)

# Organization monthly totals
table.query(
    IndexName='OrganizationIndex', 
    KeyConditionExpression=Key('organization_id').eq('org_456') &
                          Key('timestamp').begins_with('2024-03')
)
```

### User Management
```python
# Find user by email
users_table.query(
    IndexName='EmailIndex',
    KeyConditionExpression=Key('email').eq('john@example.com')
)

# Get organization members
users_table.query(
    IndexName='OrganizationIndex',
    KeyConditionExpression=Key('organization_id').eq('org_456')
)
```

## Data Modeling Best Practices

### 1. Single Table Design
- CarbonTrack uses multiple tables for clear separation
- Each table has specific query patterns
- GSIs enable different access patterns

### 2. Partition Key Selection
- `user_id` distributes data evenly across partitions
- Supports individual user workloads efficiently
- Organization queries use GSI to avoid hot partitions

### 3. Sort Key Strategy
- `timestamp` enables chronological queries
- Natural ordering for time-series data
- Efficient range queries for date periods

### 4. Attribute Design
- Denormalized structure reduces query complexity
- All emission calculation results stored together
- Metadata field for extensibility

## Scaling Considerations

### Read/Write Patterns
- **Writes**: New emissions entries (append-only)
- **Reads**: Dashboard queries, reports, analytics
- **Hot data**: Recent emissions (last 30 days)
- **Cold data**: Historical data (archive strategy)

### Performance Optimizations
- GSIs for different query patterns
- Composite sort keys for complex queries
- Item size optimization (<400KB per item)
- Batch operations for bulk imports

### Cost Optimization
- Pay-per-request billing for variable workloads
- TTL for automatic data expiration
- Projection optimization in GSIs
- Efficient query patterns to minimize RCU/WCU

## Security Model

### Access Patterns
- Individual users: Own data only
- Organization admins: Department/team data
- System admin: Platform-wide access

### IAM Policies
```json
{
  "Effect": "Allow",
  "Action": [
    "dynamodb:GetItem",
    "dynamodb:PutItem", 
    "dynamodb:Query"
  ],
  "Resource": "arn:aws:dynamodb:region:account:table/CarbonDataTable",
  "Condition": {
    "ForAllValues:StringEquals": {
      "dynamodb:LeadingKeys": ["${cognito-identity.amazonaws.com:sub}"]
    }
  }
}
```

This ensures users can only access their own data using Cognito identity as partition key.

## Migration Strategy

### Phase 1: MVP (Current)
- Single user data storage
- Basic CRUD operations
- Simple queries by user/date

### Phase 2: Multi-tenant
- Organization-level data
- Department grouping
- Role-based access

### Phase 3: Analytics
- Time-series optimizations
- Aggregation tables
- Data warehouse integration

### Phase 4: Global Scale  
- Multi-region deployment
- DynamoDB Global Tables
- Cross-region replication