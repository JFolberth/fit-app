"""
Unit tests for AI coach Pydantic models.

Tests DailyRecommendation, WorkoutDetails, TrainingContext validation
and the fallback recommendation generator.
"""

from datetime import date

import pytest

from shared.models import (
    DailyRecommendation,
    TrainingContext,
    WorkoutDetails,
    get_fallback_recommendation,
)


class TestWorkoutDetails:
    """Tests for WorkoutDetails model validation."""
    
    def test_valid_running_workout(self):
        """Valid running workout should pass validation."""
        workout = WorkoutDetails(
            type="Running",
            durationMinutes=45,
            details=["Easy pace for 35 minutes", "Cool down 10 minutes"]
        )
        assert workout.type == "Running"
        assert workout.durationMinutes == 45
        assert len(workout.details) == 2
    
    def test_valid_rest_workout(self):
        """Valid rest day should pass validation."""
        workout = WorkoutDetails(
            type="Rest",
            durationMinutes=0,
            details=["Complete rest day - focus on recovery"]
        )
        assert workout.type == "Rest"
        assert workout.durationMinutes == 0
    
    def test_invalid_workout_type(self):
        """Invalid workout type should fail validation."""
        with pytest.raises(ValueError):
            WorkoutDetails(
                type="Swimming",  # Invalid
                durationMinutes=30,
                details=["Swim laps"]
            )
    
    def test_duration_too_long(self):
        """Duration over 240 minutes should fail validation."""
        with pytest.raises(ValueError):
            WorkoutDetails(
                type="Running",
                durationMinutes=300,  # Over 240
                details=["Ultra marathon"]
            )
    
    def test_negative_duration(self):
        """Negative duration should fail validation."""
        with pytest.raises(ValueError):
            WorkoutDetails(
                type="Running",
                durationMinutes=-10,
                details=["Impossible"]
            )
    
    def test_empty_details(self):
        """Empty details array should fail validation."""
        with pytest.raises(ValueError):
            WorkoutDetails(
                type="Running",
                durationMinutes=30,
                details=[]  # min_length=1
            )
    
    def test_too_many_details(self):
        """More than 10 detail items should fail validation."""
        with pytest.raises(ValueError):
            WorkoutDetails(
                type="Running",
                durationMinutes=60,
                details=[f"Step {i}" for i in range(11)]  # max_length=10
            )


class TestDailyRecommendation:
    """Tests for DailyRecommendation model validation."""
    
    def test_valid_recommendation(self):
        """Valid recommendation should pass validation."""
        rec = DailyRecommendation(
            date=date(2026, 2, 3),
            goal="half-marathon",
            title="Easy aerobic run",
            workout=WorkoutDetails(
                type="Running",
                durationMinutes=45,
                details=["Easy pace for 45 minutes"]
            ),
            rationale="Recovery after yesterday's hard session.",
            confidence="medium",
            fallback=False
        )
        assert rec.date == date(2026, 2, 3)
        assert rec.goal == "half-marathon"
        assert rec.confidence == "medium"
        assert rec.fallback is False
    
    def test_title_too_long(self):
        """Title over 100 characters should fail validation."""
        with pytest.raises(ValueError):
            DailyRecommendation(
                date=date.today(),
                goal="half-marathon",
                title="A" * 101,  # Over 100 chars
                workout=WorkoutDetails(
                    type="Running",
                    durationMinutes=30,
                    details=["Run"]
                ),
                rationale="Test",
                confidence="low",
                fallback=True
            )
    
    def test_rationale_too_long(self):
        """Rationale over 500 characters should fail validation."""
        with pytest.raises(ValueError):
            DailyRecommendation(
                date=date.today(),
                goal="half-marathon",
                title="Test",
                workout=WorkoutDetails(
                    type="Running",
                    durationMinutes=30,
                    details=["Run"]
                ),
                rationale="A" * 501,  # Over 500 chars
                confidence="low",
                fallback=True
            )
    
    def test_invalid_confidence(self):
        """Invalid confidence level should fail validation."""
        with pytest.raises(ValueError):
            DailyRecommendation(
                date=date.today(),
                goal="half-marathon",
                title="Test",
                workout=WorkoutDetails(
                    type="Running",
                    durationMinutes=30,
                    details=["Run"]
                ),
                rationale="Test",
                confidence="very-high",  # Invalid
                fallback=True
            )
    
    def test_json_serialization(self):
        """Recommendation should serialize to JSON correctly."""
        rec = DailyRecommendation(
            date=date(2026, 2, 3),
            goal="half-marathon",
            title="Easy run",
            workout=WorkoutDetails(
                type="Running",
                durationMinutes=45,
                details=["Easy pace"]
            ),
            rationale="Recovery day.",
            confidence="high",
            fallback=False
        )
        json_data = rec.model_dump(mode="json")
        assert json_data["date"] == "2026-02-03"
        assert json_data["workout"]["type"] == "Running"


class TestTrainingContext:
    """Tests for TrainingContext model validation."""
    
    def test_valid_training_context(self):
        """Valid training context should pass validation."""
        ctx = TrainingContext(
            start_date=date(2026, 1, 20),
            end_date=date(2026, 2, 3),
            total_activities=8,
            total_distance_miles=52.3,
            total_duration_minutes=420,
            last_hard_workout=date(2026, 2, 1),
            last_long_run=date(2026, 1, 28),
            rest_days_count=3,
            activity_types=["Running", "Cross-training"]
        )
        assert ctx.total_activities == 8
        assert ctx.total_distance_miles == 52.3
    
    def test_no_activities(self):
        """Context with no activities should be valid."""
        ctx = TrainingContext(
            start_date=date(2026, 1, 20),
            end_date=date(2026, 2, 3),
            total_activities=0,
            total_distance_miles=0.0,
            total_duration_minutes=0,
            rest_days_count=14,
            activity_types=[]
        )
        assert ctx.total_activities == 0
        assert ctx.last_hard_workout is None
    
    def test_negative_distance_invalid(self):
        """Negative distance should fail validation."""
        with pytest.raises(ValueError):
            TrainingContext(
                start_date=date(2026, 1, 20),
                end_date=date(2026, 2, 3),
                total_activities=1,
                total_distance_miles=-5.0,  # Invalid
                total_duration_minutes=30,
                rest_days_count=0,
                activity_types=["Running"]
            )


class TestFallbackRecommendation:
    """Tests for fallback recommendation generator."""
    
    def test_fallback_uses_today_by_default(self):
        """Fallback should use today's date when not specified."""
        rec = get_fallback_recommendation()
        assert rec.date == date.today()
        assert rec.fallback is True
    
    def test_fallback_uses_provided_date(self):
        """Fallback should use provided date."""
        test_date = date(2026, 3, 15)
        rec = get_fallback_recommendation(today=test_date)
        assert rec.date == test_date
    
    def test_fallback_has_safe_defaults(self):
        """Fallback should have safe workout defaults."""
        rec = get_fallback_recommendation()
        assert rec.goal == "half-marathon"
        assert rec.title == "Easy aerobic run"
        assert rec.workout.type == "Running"
        assert rec.workout.durationMinutes == 45
        assert rec.confidence == "low"
        assert rec.fallback is True
    
    def test_fallback_is_valid_model(self):
        """Fallback should produce a valid DailyRecommendation."""
        rec = get_fallback_recommendation()
        # Should not raise any validation errors
        assert isinstance(rec, DailyRecommendation)
        # Should serialize to JSON without error
        json_data = rec.model_dump(mode="json")
        assert "date" in json_data
        assert "workout" in json_data
