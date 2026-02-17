from datetime import date, datetime, timedelta, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

ALLOWED_TYPES = {'Running', 'Rowing', 'Rucking'}

ONE_YEAR = timedelta(days=365)

class ActivityBase(BaseModel):
    type: str
    duration: float = Field(..., gt=0)
    distance: Optional[float] = Field(None, gt=0)
    avgBpm: int = Field(..., ge=20, le=240)
    comments: Optional[str] = None
    date: str = Field(default_factory=lambda: date.today().isoformat())

    @field_validator('type')
    def validate_type(cls, v: str) -> str:
        if v not in ALLOWED_TYPES:
            raise ValueError('type must be one of Running, Rowing, Rucking')
        return v

    @field_validator('distance', mode='before')
    def coerce_distance(cls, v):
        """Handle empty strings and convert to None."""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == '':
                return None
            try:
                return float(v)
            except ValueError:
                raise ValueError('distance must be a valid number')
        return v

    @field_validator('duration', mode='before')
    def coerce_duration(cls, v):
        """Handle string input and convert to float."""
        if v is None:
            raise ValueError('duration is required')
        if isinstance(v, str):
            v = v.strip()
            if v == '':
                raise ValueError('duration is required')
            try:
                return float(v)
            except ValueError:
                raise ValueError('duration must be a valid number')
        return v

    @field_validator('type')
    def validate_type(cls, v: str) -> str:
        if v not in ALLOWED_TYPES:
            raise ValueError('type must be one of Running, Rowing, Rucking')
        return v

    @field_validator('comments')
    def sanitize_comments(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize comments field to prevent injection attacks."""
        if v is None:
            return v
        # Limit length to prevent abuse
        if len(v) > 1000:
            raise ValueError('Comments cannot exceed 1000 characters')
        # Strip any leading/trailing whitespace
        v = v.strip()
        # Basic XSS prevention: no HTML tags
        if '<' in v or '>' in v:
            raise ValueError('Comments cannot contain HTML tags')
        return v

    @field_validator('date')
    def validate_date_bounds(cls, v: str) -> str:
        try:
            d = date.fromisoformat(v)
        except Exception:
            raise ValueError('date must be ISO format YYYY-MM-DD')
        today = date.today()
        if d > today:
            raise ValueError('Activity date cannot be in the future')
        if (today - d) > ONE_YEAR:
            raise ValueError('Activity date cannot be more than one year in the past')
        return v

    @model_validator(mode='after')
    def validate_distance_for_type(self):
        t = self.type
        v = self.distance
        if t in ('Running', 'Rucking') and v is None:
            raise ValueError('Distance is required for Running and Rucking')
        if t == 'Rowing' and v is not None:
            raise ValueError('Distance must be omitted/null for Rowing')
        return self

class ActivityCreate(ActivityBase):
    pass

class Activity(ActivityBase):
    id: str
    userId: str
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    updatedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))


def validate_activity_payload(payload: dict) -> ActivityCreate:
    """Validate incoming payload for activity creation/update according to spec rules."""
    return ActivityCreate(**payload)
