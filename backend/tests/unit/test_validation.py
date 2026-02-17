"""Unit tests for validation module."""
from datetime import date, timedelta
import pytest
from pydantic import ValidationError
from shared.validation import (
    validate_activity_payload,
    Activity,
    ActivityCreate,
    ALLOWED_TYPES,
)


class TestActivityValidation:
    """Test suite for activity validation logic."""

    def test_valid_running_activity(self):
        """Valid Running activity with all required fields."""
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 150,
            "date": "2026-01-22",
        }
        activity = validate_activity_payload(payload)
        assert activity.type == "Running"
        assert activity.duration == 1800
        assert activity.distance == 5.0
        assert activity.avgBpm == 150
        assert activity.date == "2026-01-22"

    def test_valid_rowing_activity_no_distance(self):
        """Valid Rowing activity without distance (distance prohibited)."""
        payload = {
            "type": "Rowing",
            "duration": 2400,
            "avgBpm": 140,
            "date": "2026-01-20",
        }
        activity = validate_activity_payload(payload)
        assert activity.type == "Rowing"
        assert activity.distance is None

    def test_valid_rucking_activity(self):
        """Valid Rucking activity with distance."""
        payload = {
            "type": "Rucking",
            "duration": 3600,
            "distance": 10.5,
            "avgBpm": 130,
            "comments": "Backpack training",
        }
        activity = validate_activity_payload(payload)
        assert activity.type == "Rucking"
        assert activity.comments == "Backpack training"

    def test_invalid_type(self):
        """Activity type not in ALLOWED_TYPES should fail."""
        payload = {
            "type": "Swimming",
            "duration": 1800,
            "avgBpm": 150,
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "type must be one of" in str(exc.value)

    def test_missing_distance_for_running(self):
        """Running without distance should fail."""
        payload = {
            "type": "Running",
            "duration": 1800,
            "avgBpm": 150,
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "Distance is required" in str(exc.value)

    def test_distance_provided_for_rowing(self):
        """Rowing with distance should fail."""
        payload = {
            "type": "Rowing",
            "duration": 2400,
            "distance": 5.0,
            "avgBpm": 140,
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "Distance must be omitted" in str(exc.value)

    def test_negative_duration(self):
        """Duration must be positive."""
        payload = {
            "type": "Running",
            "duration": -100,
            "distance": 5.0,
            "avgBpm": 150,
        }
        with pytest.raises(ValidationError):
            validate_activity_payload(payload)

    def test_zero_duration(self):
        """Duration must be greater than zero."""
        payload = {
            "type": "Running",
            "duration": 0,
            "distance": 5.0,
            "avgBpm": 150,
        }
        with pytest.raises(ValidationError):
            validate_activity_payload(payload)

    def test_avgbpm_too_low(self):
        """avgBpm below 20 should fail."""
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 15,
        }
        with pytest.raises(ValidationError):
            validate_activity_payload(payload)

    def test_avgbpm_too_high(self):
        """avgBpm above 240 should fail."""
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 250,
        }
        with pytest.raises(ValidationError):
            validate_activity_payload(payload)

    def test_future_date(self):
        """Activity date in the future should fail."""
        future = (date.today() + timedelta(days=1)).isoformat()
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 150,
            "date": future,
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "cannot be in the future" in str(exc.value)

    def test_date_too_old(self):
        """Activity date more than one year in the past should fail."""
        old_date = (date.today() - timedelta(days=366)).isoformat()
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 150,
            "date": old_date,
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "more than one year" in str(exc.value)

    def test_invalid_date_format(self):
        """Non-ISO date format should fail."""
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 150,
            "date": "01/22/2026",
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "ISO format" in str(exc.value)

    def test_date_defaults_to_today(self):
        """If date is omitted, should default to today."""
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 150,
        }
        activity = validate_activity_payload(payload)
        assert activity.date == date.today().isoformat()

    def test_comments_optional(self):
        """Comments field is optional."""
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 150,
        }
        activity = validate_activity_payload(payload)
        assert activity.comments is None

    def test_activity_model_with_id(self):
        """Activity model includes id, userId, createdAt, updatedAt."""
        activity = Activity(
            id="test-123",
            userId="user-456",
            type="Running",
            duration=1800,
            distance=5.0,
            avgBpm=150,
        )
        assert activity.id == "test-123"
        assert activity.userId == "user-456"
        assert activity.createdAt is not None
        assert activity.updatedAt is not None
        assert activity.createdAt.endswith("Z")


class TestCommentsSanitization:
    """Test suite for comments field sanitization."""

    def test_comments_with_html_tags_rejected(self):
        """Comments containing HTML tags should be rejected."""
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 150,
            "comments": "<script>alert('xss')</script>",
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "cannot contain HTML tags" in str(exc.value)

    def test_comments_too_long_rejected(self):
        """Comments exceeding 1000 characters should be rejected."""
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 150,
            "comments": "a" * 1001,
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "cannot exceed 1000 characters" in str(exc.value)

    def test_comments_exactly_1000_chars_accepted(self):
        """Comments with exactly 1000 characters should be accepted."""
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 150,
            "comments": "a" * 1000,
        }
        activity = validate_activity_payload(payload)
        assert len(activity.comments) == 1000

    def test_comments_whitespace_stripped(self):
        """Leading and trailing whitespace in comments should be stripped."""
        payload = {
            "type": "Running",
            "duration": 1800,
            "distance": 5.0,
            "avgBpm": 150,
            "comments": "  Good run today  ",
        }
        activity = validate_activity_payload(payload)
        assert activity.comments == "Good run today"


class TestAllowedTypes:
    """Test ALLOWED_TYPES constant."""

    def test_allowed_types_set(self):
        """Verify ALLOWED_TYPES contains expected values."""
        assert ALLOWED_TYPES == {"Running", "Rowing", "Rucking"}


class TestDistanceCoercion:
    """Test distance field coercion and optional handling."""

    def test_rowing_with_empty_string_distance(self):
        """Rowing with empty string distance should succeed (distance becomes None)."""
        payload = {
            "type": "Rowing",
            "duration": 30,
            "distance": "",
            "avgBpm": 140,
        }
        activity = validate_activity_payload(payload)
        assert activity.type == "Rowing"
        assert activity.distance is None

    def test_rowing_with_whitespace_distance(self):
        """Rowing with whitespace-only distance should succeed."""
        payload = {
            "type": "Rowing",
            "duration": 30,
            "distance": "   ",
            "avgBpm": 140,
        }
        activity = validate_activity_payload(payload)
        assert activity.distance is None

    def test_rowing_with_null_distance(self):
        """Rowing with explicit None distance should succeed."""
        payload = {
            "type": "Rowing",
            "duration": 30,
            "distance": None,
            "avgBpm": 140,
        }
        activity = validate_activity_payload(payload)
        assert activity.distance is None

    def test_distance_accepts_decimal_values(self):
        """Distance should accept decimal values like 3.14."""
        payload = {
            "type": "Running",
            "duration": 30,
            "distance": 3.14,
            "avgBpm": 150,
        }
        activity = validate_activity_payload(payload)
        assert activity.distance == 3.14

    def test_distance_accepts_decimal_string(self):
        """Distance should accept decimal values as strings."""
        payload = {
            "type": "Running",
            "duration": 30,
            "distance": "5.25",
            "avgBpm": 150,
        }
        activity = validate_activity_payload(payload)
        assert activity.distance == 5.25

    def test_distance_invalid_string_rejected(self):
        """Distance with non-numeric string should be rejected."""
        payload = {
            "type": "Running",
            "duration": 30,
            "distance": "abc",
            "avgBpm": 150,
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "valid number" in str(exc.value)

    def test_running_empty_distance_rejected(self):
        """Running with empty distance should be rejected (distance required)."""
        payload = {
            "type": "Running",
            "duration": 30,
            "distance": "",
            "avgBpm": 150,
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "Distance is required" in str(exc.value)


class TestDurationCoercion:
    """Test duration field coercion for seconds support."""

    def test_duration_accepts_decimal_minutes(self):
        """Duration should accept decimal values for seconds (e.g., 30.5 = 30min 30sec)."""
        payload = {
            "type": "Rowing",
            "duration": 30.5,
            "avgBpm": 140,
        }
        activity = validate_activity_payload(payload)
        assert activity.duration == 30.5

    def test_duration_accepts_small_decimals(self):
        """Duration should accept values like 0.5 (30 seconds)."""
        payload = {
            "type": "Rowing",
            "duration": 0.5,
            "avgBpm": 140,
        }
        activity = validate_activity_payload(payload)
        assert activity.duration == 0.5

    def test_duration_accepts_precise_seconds(self):
        """Duration should accept precise values like 45.75 (45min 45sec)."""
        payload = {
            "type": "Rowing",
            "duration": 45.75,
            "avgBpm": 140,
        }
        activity = validate_activity_payload(payload)
        assert activity.duration == 45.75

    def test_duration_as_string(self):
        """Duration should accept string values and convert."""
        payload = {
            "type": "Rowing",
            "duration": "30.25",
            "avgBpm": 140,
        }
        activity = validate_activity_payload(payload)
        assert activity.duration == 30.25

    def test_duration_empty_string_rejected(self):
        """Duration with empty string should be rejected."""
        payload = {
            "type": "Rowing",
            "duration": "",
            "avgBpm": 140,
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "duration is required" in str(exc.value)

    def test_duration_invalid_string_rejected(self):
        """Duration with non-numeric string should be rejected."""
        payload = {
            "type": "Rowing",
            "duration": "thirty",
            "avgBpm": 140,
        }
        with pytest.raises(ValidationError) as exc:
            validate_activity_payload(payload)
        assert "valid number" in str(exc.value)
