# Recommendations & Achievements Implementation

This module provides intelligent carbon reduction recommendations and gamification features.

## Implementation Status: ✅ COMPLETE

## Recommendations System

### Intelligence Engine
- Analyzes user emission patterns across categories
- Calculates personalized reduction opportunities
- Scores recommendations by relevance and impact
- Updates dynamically based on user behavior

### API Endpoints
- `GET /api/v1/recommendations/` - Get personalized recommendations
- `GET /api/v1/recommendations/stats` - Get recommendation statistics  
- `POST /api/v1/recommendations/{id}/track` - Track recommendation adoption

### Recommendation Categories
1. **Transportation** (🚗)
   - Electric/hybrid vehicle suggestions
   - Public transport alternatives
   - Carpooling and trip optimization

2. **Energy** (⚡)
   - LED lighting upgrades
   - Smart thermostat installation
   - Renewable energy options

3. **Food** (🍽️)
   - Plant-based meal suggestions
   - Local food sourcing
   - Meal planning for waste reduction

4. **Waste** (♻️)
   - Composting programs
   - Recycling optimization
   - Zero-waste initiatives

## Achievements System

### Gamification Features
- **Levels**: 1-50 based on total points
- **Points**: Earned through emissions tracking and reductions
- **Badges**: 25+ achievements across categories
- **Challenges**: Weekly and monthly goals

### Achievement Types

#### Tracking Achievements
- First Entry
- 10 Entries
- 50 Entries  
- 100 Entries
- Consistent Tracker (7 days streak)
- Data Champion (30 days streak)

#### Reduction Achievements
- Quick Win (5% reduction)
- Getting Better (10% reduction)
- Making Progress (25% reduction)
- Eco Warrior (50% reduction)
- Carbon Hero (75% reduction)

#### Category Achievements
- Transportation Master
- Energy Saver
- Food Conscious
- Waste Warrior
- Eco All-Rounder

### API Endpoints
- `GET /api/v1/gamification/profile` - Get user level, points, badges
- `GET /api/v1/gamification/achievements` - Get all achievements with progress
- `GET /api/v1/gamification/leaderboards` - Get top users
- `POST /api/v1/gamification/challenges/{id}/complete` - Complete challenge

## Database Schema

### Recommendations Table
```
carbontrack-recommendations
- userId (PK)
- recommendationId (SK)
- category
- title
- description
- potential_savings_kg
- relevance_score
- status (pending/adopted/dismissed)
- created_at
- updated_at
```

### Achievements Table  
```
carbontrack-achievements
- userId (PK)
- achievementId (SK)
- type
- title
- description
- requirement
- progress
- is_unlocked
- unlocked_at
```

### Gamification Profile Table
```
carbontrack-gamification
- userId (PK)
- level
- total_points
- current_streak
- longest_streak
- badges[]
- challenges_completed
- created_at
- updated_at
```

## Points System

### Activity Points
- Entry logged: +10 points
- Daily goal met: +25 points
- Weekly goal met: +50 points
- Monthly goal met: +100 points
- Recommendation adopted: +30 points

### Reduction Bonuses
- 5% reduction: +50 points
- 10% reduction: +100 points
- 25% reduction: +250 points
- 50% reduction: +500 points

### Level Calculation
```
Level = floor(sqrt(total_points / 100))
```

## Frontend Integration

### Components
- `RecommendationsView` - Display personalized suggestions
- `AchievementsView` - Show badges and progress
- `LeaderboardView` - Competitive rankings
- `ChallengesView` - Active and completed challenges

### State Management
- User gamification profile cached in localStorage
- Real-time updates on achievement unlocks
- Notification system for new badges
- Progress bars for ongoing challenges
