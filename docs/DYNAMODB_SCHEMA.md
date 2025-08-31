# DynamoDB Schema Documentation for CarbonTrack

## Overview

This document describes the DynamoDB schema design for the CarbonTrack application. The schema is designed to efficiently store user profiles, carbon footprint data, goals, and achievements while supporting fast queries and analytics.

## Table Design Philosophy

- **Single-table design considerations**: Each entity type has its own table for simplicity and clear separation of concerns
- **Partition key strategy**: User-centric partitioning to ensure data locality and efficient queries
- **Sort key strategy**: Time-based and ID-based sorting for chronological and unique access patterns
- **Billing mode**: PAY_PER_REQUEST for development, can be changed to PROVISIONED for production

## Tables Overview

| Table Name | Partition Key | Sort Key | Purpose |
|------------|---------------|----------|---------|
| carbontrack-users | userId (S) | - | User profiles and settings |
| carbontrack-entries | userId (S) | timestamp (S) | Carbon footprint entries |
| carbontrack-goals | userId (S) | goalId (S) | User carbon reduction goals |
| carbontrack-achievements | userId (S) | achievementId (S) | User achievements and badges |

## Detailed Schema

### 1. carbontrack-users

**Purpose**: Store user profiles, preferences, and aggregated statistics

**Primary Key**: 
- Partition Key: `userId` (String) - Cognito User ID

**Attributes**:
```json
{
  "user_id": "2344f892-50a1-7096-e5ad-002f58f36b58",
  "email": "user@example.com",
  "full_name": "John Doe",
  "avatar_url": "https://example.com/avatar.jpg",
  "preferred_units": {
    "distance": "km",
    "energy": "kWh", 
    "weight": "kg"
  },
  "carbon_budget": 500.0,
  "total_emissions": 1250.75,
  "current_month_emissions": 125.50,
  "entries_count": 45,
  "created_at": "2025-08-31T10:00:00Z",
  "updated_at": "2025-08-31T15:30:00Z",
  "last_active": "2025-08-31T15:30:00Z"
}
```

**Access Patterns**:
- Get user profile by userId
- Update user statistics
- Update user preferences

### 2. carbontrack-entries

**Purpose**: Store individual carbon footprint entries

**Primary Key**:
- Partition Key: `userId` (String) - Groups all entries by user
- Sort Key: `timestamp` (String) - ISO datetime for chronological ordering

**Attributes**:
```json
{
  "userId": "2344f892-50a1-7096-e5ad-002f58f36b58",
  "timestamp": "2025-08-31T10:15:00Z",
  "entry_id": "550e8400-e29b-41d4-a716-446655440000",
  "date": "2025-08-31",
  "category": "transportation",
  "activity": "car_drive",
  "amount": 25.5,
  "unit": "km",
  "description": "Daily commute to office",
  "co2_equivalent": 5.1,
  "emission_factor": 0.2,
  "created_at": "2025-08-31T10:15:00Z",
  "updated_at": "2025-08-31T10:15:00Z"
}
```

**Access Patterns**:
- Get all entries for a user (chronologically ordered)
- Get entries within a date range
- Update/delete specific entry by userId + timestamp
- Query for analytics (by category, time period)

**Categories**:
- `transportation` - Cars, flights, public transport
- `energy` - Electricity, heating, cooling
- `food` - Meals, groceries
- `waste` - Recycling, disposal
- `other` - Miscellaneous activities

### 3. carbontrack-goals

**Purpose**: Store user-defined carbon reduction goals

**Primary Key**:
- Partition Key: `userId` (String)
- Sort Key: `goalId` (String) - UUID for each goal

**Attributes**:
```json
{
  "userId": "2344f892-50a1-7096-e5ad-002f58f36b58",
  "goalId": "goal-550e8400-e29b-41d4-a716-446655440000",
  "category": "transportation",
  "target_amount": 100.0,
  "target_period": "monthly",
  "description": "Reduce transportation emissions to 100kg CO2 per month",
  "current_amount": 75.5,
  "is_active": true,
  "is_achieved": false,
  "start_date": "2025-08-01",
  "end_date": "2025-08-31",
  "achieved_date": null,
  "created_at": "2025-08-01T00:00:00Z",
  "updated_at": "2025-08-31T10:15:00Z"
}
```

**Access Patterns**:
- Get all goals for a user
- Get active goals only
- Update goal progress
- Mark goals as achieved

**Target Periods**:
- `daily` - Daily targets
- `weekly` - Weekly targets  
- `monthly` - Monthly targets
- `yearly` - Annual targets

### 4. carbontrack-achievements

**Purpose**: Store user achievements and progress tracking

**Primary Key**:
- Partition Key: `userId` (String)
- Sort Key: `achievementId` (String) - UUID for each achievement

**Attributes**:
```json
{
  "userId": "2344f892-50a1-7096-e5ad-002f58f36b58",
  "achievementId": "achievement-550e8400-e29b-41d4-a716-446655440000",
  "title": "First Steps",
  "description": "Created your first carbon footprint entry",
  "category": "milestone",
  "icon": "🌱",
  "requirement_type": "entries",
  "requirement_value": 1,
  "current_progress": 1,
  "is_unlocked": true,
  "unlocked_date": "2025-08-31T10:15:00Z",
  "created_at": "2025-08-31T10:15:00Z",
  "updated_at": "2025-08-31T10:15:00Z"
}
```

**Access Patterns**:
- Get all achievements for a user
- Get unlocked achievements
- Update achievement progress

**Achievement Categories**:
- `milestone` - Entry count milestones
- `reduction` - Emission reduction achievements  
- `streak` - Consecutive day achievements
- `category` - Category-specific achievements

## Query Patterns

### Common Queries

1. **Get user profile**:
   ```python
   users_table.get_item(Key={'user_id': user_id})
   ```

2. **Get recent entries**:
   ```python
   entries_table.query(
       KeyConditionExpression='userId = :user_id',
       ExpressionAttributeValues={':user_id': user_id},
       ScanIndexForward=False,  # Latest first
       Limit=20
   )
   ```

3. **Get entries in date range**:
   ```python
   entries_table.query(
       KeyConditionExpression='userId = :user_id AND #ts BETWEEN :start AND :end',
       ExpressionAttributeValues={
           ':user_id': user_id,
           ':start': '2025-08-01T00:00:00Z',
           ':end': '2025-08-31T23:59:59Z'
       },
       ExpressionAttributeNames={'#ts': 'timestamp'}
   )
   ```

4. **Get active goals**:
   ```python
   goals_table.query(
       KeyConditionExpression='userId = :user_id',
       FilterExpression='is_active = :active',
       ExpressionAttributeValues={
           ':user_id': user_id,
           ':active': True
       }
   )
   ```

## Performance Considerations

### Partition Design
- **Hot partitions**: Users with high activity might create hot partitions. Consider sharding strategies if needed.
- **Partition size**: Each user's data should stay well under 10GB limit per partition.

### Query Efficiency
- **Sort key usage**: Always use sort key ranges when possible to limit scanned items
- **Projection**: Use projection expressions to fetch only needed attributes
- **Pagination**: Implement pagination for large result sets

### Cost Optimization
- **Sparse attributes**: Only store attributes that have values
- **Data compression**: Consider compressing large text fields
- **TTL**: Implement TTL for temporary data if applicable

## Indexes

Currently, no Global Secondary Indexes (GSIs) are defined. Consider adding if needed:

### Potential GSIs

1. **CategoryIndex** on carbontrack-entries:
   - Partition Key: `category`
   - Sort Key: `timestamp`
   - Use case: Global category analytics

2. **DateIndex** on carbontrack-entries:
   - Partition Key: `date`  
   - Sort Key: `userId`
   - Use case: Daily global statistics

## Data Types and Validation

### DynamoDB Data Types Used
- **S** (String): IDs, text, dates, timestamps
- **N** (Number): Amounts, counts, calculations
- **BOOL** (Boolean): Flags and status
- **M** (Map): Nested objects like preferences
- **NULL**: Optional fields

### Validation Rules
- `userId`: Must be valid Cognito User ID
- `timestamp`: Must be valid ISO 8601 datetime
- `amount`: Must be positive number
- `category`: Must be from predefined list
- `target_period`: Must be from predefined list

## Backup and Recovery

### Backup Strategy
- **Point-in-time recovery**: Enable for production tables
- **On-demand backups**: For major releases
- **Cross-region backups**: For disaster recovery

### Data Retention
- **User data**: Retain indefinitely (user-controlled deletion)
- **Carbon entries**: Retain indefinitely for historical analysis
- **Goals**: Retain completed goals for progress tracking
- **Achievements**: Retain permanently

## Testing Strategy

### Unit Tests
- Test each CRUD operation
- Test query patterns
- Test error handling

### Integration Tests  
- Test with sample Lambda function
- Validate data consistency
- Performance testing with realistic data volumes

### Load Testing
- Test partition key distribution
- Validate performance under load
- Test auto-scaling behavior

## Migration Strategy

### Initial Setup
1. Create tables using provided script
2. Set up IAM roles and permissions
3. Deploy test Lambda function
4. Validate all operations

### Schema Evolution
- Use application-level versioning
- Maintain backward compatibility
- Plan for gradual migrations

## Security

### Access Control
- **IAM policies**: Restrict access by table and operation
- **User isolation**: Ensure users can only access their own data
- **Encryption**: Enable encryption at rest and in transit

### Data Privacy
- **PII handling**: Follow GDPR guidelines for user data
- **Data anonymization**: For analytics and research
- **Audit logging**: Track all data access and modifications

## Monitoring and Alerting

### Key Metrics
- **Read/Write capacity utilization**
- **Throttling events**
- **Query performance**
- **Error rates**

### Alerts
- **High throttling**: Indicates capacity issues
- **High latency**: Performance degradation
- **Error spikes**: Application issues
- **Unusual access patterns**: Security concerns
