"""
Training context builder for AI coach feature.

Builds a TrainingContext summary from recent activity data retrieved via MCP.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from .models import TrainingContext


def build_training_context(
    activities: List[Dict[str, Any]],
    start_date: date,
    end_date: date
) -> TrainingContext:
    """
    Build a TrainingContext from a list of activity documents.
    
    Args:
        activities: List of activity documents from Cosmos DB
        start_date: Start of analysis window
        end_date: End of analysis window (typically today)
        
    Returns:
        TrainingContext with summarized training data
    """
    if not activities:
        return TrainingContext(
            start_date=start_date,
            end_date=end_date,
            total_activities=0,
            total_distance_miles=0.0,
            total_duration_minutes=0,
            last_hard_workout=None,
            last_long_run=None,
            rest_days_count=_count_rest_days([], start_date, end_date),
            activity_types=[]
        )
    
    # Calculate totals
    total_distance = sum(
        float(a.get("distance", 0) or 0) 
        for a in activities
    )
    total_duration = sum(
        int(a.get("duration", 0) or 0) 
        for a in activities
    )
    
    # Get unique activity types
    activity_types = list(set(
        a.get("type", "Unknown") 
        for a in activities 
        if a.get("type")
    ))
    
    # Find last hard workout (high intensity or tempo)
    last_hard = _find_last_hard_workout(activities)
    
    # Find last long run (>90 min or >15 miles)
    last_long = _find_last_long_run(activities)
    
    # Count rest days
    rest_days = _count_rest_days(activities, start_date, end_date)
    
    return TrainingContext(
        start_date=start_date,
        end_date=end_date,
        total_activities=len(activities),
        total_distance_miles=total_distance,
        total_duration_minutes=total_duration,
        last_hard_workout=last_hard,
        last_long_run=last_long,
        rest_days_count=rest_days,
        activity_types=activity_types
    )


def _find_last_hard_workout(activities: List[Dict[str, Any]]) -> Optional[date]:
    """
    Find the date of the most recent high-intensity workout.
    
    A workout is considered "hard" if:
    - Average heart rate > 160 BPM
    - Comments mention "tempo", "interval", "speed", "hard", "race"
    - Duration > 60 min with high intensity indicators
    
    Args:
        activities: List of activity documents, sorted by date descending
        
    Returns:
        Date of last hard workout, or None if not found
    """
    hard_keywords = ["tempo", "interval", "speed", "hard", "race", "fartlek", "threshold"]
    
    for activity in activities:
        # Check heart rate
        avg_bpm = activity.get("avgBpm")
        if avg_bpm and int(avg_bpm) > 160:
            return _parse_date(activity.get("date"))
        
        # Check comments for hard workout indicators
        comments = (activity.get("comments") or "").lower()
        if any(keyword in comments for keyword in hard_keywords):
            return _parse_date(activity.get("date"))
    
    return None


def _find_last_long_run(activities: List[Dict[str, Any]]) -> Optional[date]:
    """
    Find the date of the most recent long run.
    
    A run is considered "long" if:
    - Duration > 90 minutes
    - Distance > 10 miles (for running activities)
    
    Args:
        activities: List of activity documents, sorted by date descending
        
    Returns:
        Date of last long run, or None if not found
    """
    for activity in activities:
        activity_type = activity.get("type", "").lower()
        
        # Only consider running activities
        if "run" not in activity_type and activity_type != "running":
            continue
        
        duration = int(activity.get("duration", 0) or 0)
        distance = float(activity.get("distance", 0) or 0)
        
        if duration > 90 or distance > 10:
            return _parse_date(activity.get("date"))
    
    return None


def _count_rest_days(
    activities: List[Dict[str, Any]],
    start_date: date,
    end_date: date
) -> int:
    """
    Count days with no activities in the date range.
    
    Args:
        activities: List of activity documents
        start_date: Start of analysis window
        end_date: End of analysis window
        
    Returns:
        Number of rest days
    """
    # Get all dates with activities
    activity_dates = set()
    for activity in activities:
        activity_date = _parse_date(activity.get("date"))
        if activity_date:
            activity_dates.add(activity_date)
    
    # Count days without activities
    total_days = (end_date - start_date).days + 1
    active_days = len(activity_dates)
    
    return max(0, total_days - active_days)


def _parse_date(date_str: Optional[str]) -> Optional[date]:
    """
    Parse a date string to a date object.
    
    Args:
        date_str: ISO format date string (YYYY-MM-DD)
        
    Returns:
        date object or None if invalid
    """
    if not date_str:
        return None
    
    try:
        # Handle ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS
        date_part = date_str.split("T")[0]
        return date.fromisoformat(date_part)
    except (ValueError, AttributeError):
        return None
