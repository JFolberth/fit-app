"""
Pydantic models for AI coach feature.

Defines DailyRecommendation, WorkoutDetails, TrainingContext and fallback generator.
"""

from datetime import date as date_type
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class WorkoutDetails(BaseModel):
    """Structured workout instructions."""
    
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


class DailyRecommendation(BaseModel):
    """Complete daily workout recommendation for half marathon training."""
    
    date: date_type = Field(
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
    fallback_reason: Optional[Literal["ai_unavailable", "mcp_unavailable", "timeout", "error"]] = Field(
        default=None,
        description="Reason for fallback: ai_unavailable (AI Foundry connection failed), mcp_unavailable (MCP server unavailable), timeout (request timed out), error (unexpected error)"
    )


class TrainingContext(BaseModel):
    """Internal data structure summarizing recent activities for AI agent prompt."""
    
    start_date: date_type = Field(
        description="Start of analysis window (e.g., today - 14 days)"
    )
    end_date: date_type = Field(
        description="End of analysis window (today)"
    )
    total_activities: int = Field(
        ge=0,
        description="Total number of activities in window"
    )
    total_distance_miles: float = Field(
        ge=0,
        description="Total distance covered (miles)"
    )
    total_duration_minutes: int = Field(
        ge=0,
        description="Total workout duration (minutes)"
    )
    last_hard_workout: Optional[date_type] = Field(
        default=None,
        description="Date of last high-intensity workout"
    )
    last_long_run: Optional[date_type] = Field(
        default=None,
        description="Date of last long run (>90 min or >15km)"
    )
    rest_days_count: int = Field(
        ge=0,
        description="Number of rest days in window"
    )
    activity_types: List[str] = Field(
        default_factory=list,
        description="Distinct activity types logged"
    )


def get_fallback_recommendation(
    today: Optional[date_type] = None,
    reason: Optional[str] = None
) -> DailyRecommendation:
    """
    Generate a safe fallback recommendation when AI agent is unavailable.
    
    Args:
        today: The date for the recommendation. Defaults to current date.
        reason: The reason for fallback (ai_unavailable, mcp_unavailable, timeout, error)
        
    Returns:
        A DailyRecommendation with fallback=True and a safe default workout.
    """
    if today is None:
        today = date_type.today()
    
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
        fallback=True,
        fallback_reason=reason
    )
