# Data Model: AI Daily Half Marathon Coach

**Feature**: AI Daily Half Marathon Coach (Home Page)  
**Branch**: `002-ai-homepage-coach`

---

## Overview

This document defines the key entities and data structures for the AI coaching feature. All models use Pydantic for validation and type safety.

---

## Core Entities

### 1. DailyRecommendation

The primary response object returned by `/api/coach/today` endpoint.

**Purpose**: Represents a complete daily workout recommendation for half marathon training.

**Schema**:
```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date

class DailyRecommendation(BaseModel):
    date: date = Field(
        description="The date for this recommendation (ISO 8601 format)"
    )
    goal: Literal["half-marathon"] = Field(
        description="Training goal"
    )
    title: str = Field(
        max_length=100,
        description="Short, descriptive title for today's workout"
    )
    workout: WorkoutDetails = Field(
        description="Detailed workout instructions"
    )
    rationale: str = Field(
        max_length=500,
        description="Brief explanation of why this workout is recommended today"
    )
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level of the recommendation"
    )
    fallback: bool = Field(
        description="True if this is a fallback recommendation (AI unavailable), false if AI-generated"
    )
```

**Example**:
```json
{
  "date": "2026-02-03",
  "goal": "half-marathon",
  "title": "Easy aerobic run + strides",
  "workout": {
    "type": "Running",
    "durationMinutes": 45,
    "details": [
      "Easy pace for 35 minutes",
      "6 x 20s strides with full recovery",
      "Cool down 5 minutes"
    ]
  },
  "rationale": "Based on your last hard run 2 days ago and total volume this week, today is best used for aerobic recovery and leg turnover.",
  "confidence": "medium",
  "fallback": false
}
```

**Validation Rules**:
- `date` must be valid ISO 8601 date
- `title` must not exceed 100 characters
- `rationale` must not exceed 500 characters
- `confidence` must be one of: "low", "medium", "high"
- `fallback` must be boolean

---

### 2. WorkoutDetails

Nested entity within `DailyRecommendation` providing workout specifics.

**Purpose**: Structure the workout instructions in a consistent, machine-readable format.

**Schema**:
```python
from pydantic import BaseModel, Field
from typing import Literal, List

class WorkoutDetails(BaseModel):
    type: Literal["Running", "Cross-training", "Rest", "Strength"] = Field(
        description="Type of workout activity"
    )
    durationMinutes: int = Field(
        ge=0,
        le=240,
        description="Recommended workout duration in minutes"
    )
    details: List[str] = Field(
        min_length=1,
        max_length=10,
        description="Step-by-step workout instructions"
    )
```

**Example**:
```json
{
  "type": "Running",
  "durationMinutes": 45,
  "details": [
    "Easy pace for 35 minutes",
    "6 x 20s strides with full recovery",
    "Cool down 5 minutes"
  ]
}
```

**Validation Rules**:
- `type` must be one of: "Running", "Cross-training", "Rest", "Strength"
- `durationMinutes` must be between 0 and 240 (4 hours max)
- `details` array must have 1-10 items

---

### 3. TrainingContext (Internal)

**Purpose**: Internal data structure summarizing recent activities for AI agent prompt.

**Schema**:
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class TrainingContext(BaseModel):
    start_date: date = Field(
        description="Start of analysis window (e.g., today - 14 days)"
    )
    end_date: date = Field(
        description="End of analysis window (today)"
    )
    total_activities: int = Field(
        ge=0,
        description="Total number of activities in window"
    )
    total_distance_km: float = Field(
        ge=0,
        description="Total distance covered (km)"
    )
    total_duration_minutes: int = Field(
        ge=0,
        description="Total workout duration (minutes)"
    )
    last_hard_workout: Optional[date] = Field(
        default=None,
        description="Date of last high-intensity workout"
    )
    last_long_run: Optional[date] = Field(
        default=None,
        description="Date of last long run (>90 min or >15km)"
    )
    rest_days_count: int = Field(
        ge=0,
        description="Number of rest days in window"
    )
    activity_types: List[str] = Field(
        description="Distinct activity types logged"
    )
```

**Example**:
```json
{
  "start_date": "2026-01-20",
  "end_date": "2026-02-03",
  "total_activities": 8,
  "total_distance_km": 52.3,
  "total_duration_minutes": 420,
  "last_hard_workout": "2026-02-01",
  "last_long_run": "2026-01-28",
  "rest_days_count": 3,
  "activity_types": ["Running", "Cross-training"]
}
```

**Usage**: Built from MCP server queries, passed to AI agent for context.

---

## Relationships

```
DailyRecommendation
├── workout: WorkoutDetails
└── (derived from) TrainingContext (internal)
```

**Data Flow**:
1. Backend queries MCP server for recent activities
2. Backend builds `TrainingContext` from activity data
3. Backend sends `TrainingContext` to AI agent
4. AI agent returns structured JSON matching `DailyRecommendation` schema
5. Backend validates with Pydantic
6. Frontend renders validated `DailyRecommendation`

---

## Storage

### Backend (Azure Functions)
- **Models Location**: `backend/functions/shared/models.py` (new file)
- **Validation**: Pydantic `BaseModel.model_validate()`
- **Serialization**: `.model_dump(mode='json')` for API responses

### Frontend (Vanilla JS)
- **Type Checking**: None (vanilla JS)
- **Validation**: Trust backend validation
- **Display**: Direct property access from JSON response

---

## Fallback Strategy

When AI agent is unavailable or returns invalid data, backend generates a deterministic fallback:

```python
def get_fallback_recommendation(today: date) -> DailyRecommendation:
    return DailyRecommendation(
        date=today,
        goal="half-marathon",
        title="Easy aerobic run",
        workout=WorkoutDetails(
            type="Running",
            durationMinutes=45,
            details=[
                "Easy conversational pace for 35-45 minutes",
                "Focus on comfortable breathing",
                "Optional: 4-6 x 20s strides"
            ]
        ),
        rationale="A moderate aerobic run is a safe default for maintaining fitness and building endurance.",
        confidence="low",
        fallback=True
    )
```

---

## Future Extensions

### Multi-Goal Support
```python
goal: Literal["half-marathon", "marathon", "5k", "10k"]
```

### User Profile Integration
```python
class UserProfile(BaseModel):
    target_race_date: Optional[date]
    weekly_mileage_target: Optional[int]
    injury_notes: Optional[str]
```

### Recommendation History
```python
class RecommendationHistory(BaseModel):
    recommendation_id: str
    user_id: str
    date: date
    recommendation: DailyRecommendation
    completed: bool
```

---

## References

- [OpenAPI Contract](contracts/openapi.yaml)
- [Implementation Plan](plan.md)
- [Pydantic Documentation](https://docs.pydantic.dev/)
