"""
Unit tests for training context builder.

Tests build_training_context function with various activity scenarios.
"""

from datetime import date, timedelta

from shared.training_context import (
    build_training_context,
    _find_last_hard_workout,
    _find_last_long_run,
    _count_rest_days,
    _parse_date,
)


class TestBuildTrainingContext:
    """Tests for build_training_context function."""
    
    def test_empty_activities(self):
        """Empty activities list should return zeroed context."""
        today = date(2026, 2, 3)
        start = today - timedelta(days=14)
        
        ctx = build_training_context([], start, today)
        
        assert ctx.total_activities == 0
        assert ctx.total_distance_miles == 0.0
        assert ctx.total_duration_minutes == 0
        assert ctx.last_hard_workout is None
        assert ctx.last_long_run is None
        assert ctx.rest_days_count == 15  # All days are rest days
        assert ctx.activity_types == []
    
    def test_single_activity(self):
        """Single activity should be counted correctly."""
        today = date(2026, 2, 3)
        start = today - timedelta(days=14)
        
        activities = [
            {
                "date": "2026-02-02",
                "type": "Running",
                "distance": 5.0,
                "duration": 45
            }
        ]
        
        ctx = build_training_context(activities, start, today)
        
        assert ctx.total_activities == 1
        assert ctx.total_distance_miles == 5.0
        assert ctx.total_duration_minutes == 45
        assert ctx.activity_types == ["Running"]
    
    def test_multiple_activities(self):
        """Multiple activities should be summed correctly."""
        today = date(2026, 2, 3)
        start = today - timedelta(days=14)
        
        activities = [
            {"date": "2026-02-02", "type": "Running", "distance": 5.0, "duration": 45},
            {"date": "2026-02-01", "type": "Running", "distance": 3.0, "duration": 30},
            {"date": "2026-01-30", "type": "Cross-training", "distance": None, "duration": 60},
        ]
        
        ctx = build_training_context(activities, start, today)
        
        assert ctx.total_activities == 3
        assert ctx.total_distance_miles == 8.0  # 5 + 3 + 0
        assert ctx.total_duration_minutes == 135  # 45 + 30 + 60
        assert set(ctx.activity_types) == {"Running", "Cross-training"}
    
    def test_handles_missing_fields(self):
        """Should handle activities with missing optional fields."""
        today = date(2026, 2, 3)
        start = today - timedelta(days=14)
        
        activities = [
            {"date": "2026-02-02", "type": "Running"},  # Missing distance/duration
            {"date": "2026-02-01"},  # Missing type/distance/duration
        ]
        
        ctx = build_training_context(activities, start, today)
        
        assert ctx.total_activities == 2
        assert ctx.total_distance_miles == 0.0
        assert ctx.total_duration_minutes == 0


class TestFindLastHardWorkout:
    """Tests for _find_last_hard_workout function."""
    
    def test_no_hard_workouts(self):
        """Should return None when no hard workouts found."""
        activities = [
            {"date": "2026-02-02", "avgBpm": 130, "comments": "Easy run"}
        ]
        assert _find_last_hard_workout(activities) is None
    
    def test_high_heart_rate(self):
        """Should detect hard workout by heart rate > 160."""
        activities = [
            {"date": "2026-02-02", "avgBpm": 175, "comments": "Morning run"}
        ]
        result = _find_last_hard_workout(activities)
        assert result == date(2026, 2, 2)
    
    def test_tempo_in_comments(self):
        """Should detect hard workout by 'tempo' in comments."""
        activities = [
            {"date": "2026-02-01", "avgBpm": 150, "comments": "Tempo run today"}
        ]
        result = _find_last_hard_workout(activities)
        assert result == date(2026, 2, 1)
    
    def test_interval_in_comments(self):
        """Should detect hard workout by 'interval' in comments."""
        activities = [
            {"date": "2026-01-30", "comments": "Track intervals 6x800m"}
        ]
        result = _find_last_hard_workout(activities)
        assert result == date(2026, 1, 30)
    
    def test_returns_most_recent(self):
        """Should return most recent hard workout (list is desc sorted)."""
        activities = [
            {"date": "2026-02-02", "avgBpm": 170},  # Most recent
            {"date": "2026-01-30", "avgBpm": 165},
        ]
        result = _find_last_hard_workout(activities)
        assert result == date(2026, 2, 2)


class TestFindLastLongRun:
    """Tests for _find_last_long_run function."""
    
    def test_no_long_runs(self):
        """Should return None when no long runs found."""
        activities = [
            {"date": "2026-02-02", "type": "Running", "duration": 45, "distance": 5}
        ]
        assert _find_last_long_run(activities) is None
    
    def test_long_duration(self):
        """Should detect long run by duration > 90 minutes."""
        activities = [
            {"date": "2026-02-02", "type": "Running", "duration": 100, "distance": 8}
        ]
        result = _find_last_long_run(activities)
        assert result == date(2026, 2, 2)
    
    def test_long_distance(self):
        """Should detect long run by distance > 10 miles."""
        activities = [
            {"date": "2026-02-01", "type": "Running", "duration": 85, "distance": 12}
        ]
        result = _find_last_long_run(activities)
        assert result == date(2026, 2, 1)
    
    def test_ignores_non_running(self):
        """Should ignore non-running activities even if long."""
        activities = [
            {"date": "2026-02-02", "type": "Cross-training", "duration": 120},
            {"date": "2026-02-01", "type": "Running", "duration": 100},
        ]
        result = _find_last_long_run(activities)
        assert result == date(2026, 2, 1)


class TestCountRestDays:
    """Tests for _count_rest_days function."""
    
    def test_all_rest_days(self):
        """No activities means all days are rest days."""
        today = date(2026, 2, 3)
        start = today - timedelta(days=6)  # 7 day window
        
        rest_days = _count_rest_days([], start, today)
        assert rest_days == 7
    
    def test_no_rest_days(self):
        """Activity every day means no rest days."""
        today = date(2026, 2, 3)
        start = today - timedelta(days=2)  # 3 day window
        
        activities = [
            {"date": "2026-02-03"},
            {"date": "2026-02-02"},
            {"date": "2026-02-01"},
        ]
        
        rest_days = _count_rest_days(activities, start, today)
        assert rest_days == 0
    
    def test_some_rest_days(self):
        """Mix of active and rest days."""
        today = date(2026, 2, 3)
        start = today - timedelta(days=6)  # 7 day window
        
        activities = [
            {"date": "2026-02-03"},
            {"date": "2026-02-01"},
            {"date": "2026-01-29"},
        ]
        
        rest_days = _count_rest_days(activities, start, today)
        assert rest_days == 4  # 7 total - 3 active


class TestParseDate:
    """Tests for _parse_date function."""
    
    def test_valid_date(self):
        """Should parse valid ISO date string."""
        assert _parse_date("2026-02-03") == date(2026, 2, 3)
    
    def test_datetime_string(self):
        """Should handle datetime string with time component."""
        assert _parse_date("2026-02-03T10:30:00") == date(2026, 2, 3)
    
    def test_none_input(self):
        """Should return None for None input."""
        assert _parse_date(None) is None
    
    def test_invalid_string(self):
        """Should return None for invalid date string."""
        assert _parse_date("not-a-date") is None
    
    def test_empty_string(self):
        """Should return None for empty string."""
        assert _parse_date("") is None
