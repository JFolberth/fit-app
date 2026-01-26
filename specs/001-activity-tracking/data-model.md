# Phase 1 Data Model: Activity Tracking

## Entities

### Activity
- id: string (UUID)
- type: enum (Running | Rowing | Rucking)
- duration: number (minutes, > 0)
- distance: number (miles, > 0; nullable for Rowing)
- avgBpm: number (20–240; optional)
- comments: string (optional, reasonable length)
- date: date (defaults to current day)
- createdAt: datetime
- updatedAt: datetime

Validation rules
- Running: require duration, distance
- Rowing: require duration (distance null)
- Rucking: require duration, distance
- All: optional avgBpm in [20,240], optional comments, date default today (reject future; reject >1 year away)

## Relationships
None beyond per-activity optional `comments` text field.

## Storage
- Azure Cosmos DB (NoSQL)
- Recommended containers:
  - activities (partition key: `/type` or `/date`)
  - comments (partition key: `/createdAt` (coarse) or `/id`)

## Indexing considerations
- Activities: composite index on `date` desc for history ordering; filter by `type`
- Comments: index on `createdAt` desc

## State transitions
- Activity: create → edit → delete
- Comment: create → delete
