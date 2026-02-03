"""
Unit tests for AI client.

Tests AIClient with mocked responses.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from shared.ai_client import AIClient, AIClientError, COACH_SYSTEM_PROMPT


class TestAIClient:
    """Tests for AIClient class."""
    
    def test_init_with_defaults(self):
        """Should initialize with default endpoint and model."""
        client = AIClient()
        assert "fit-app-resource" in client.endpoint
        assert client.model == "gpt-5-mini"
    
    def test_init_with_custom_values(self):
        """Should accept custom endpoint and model."""
        client = AIClient(
            endpoint="https://custom.endpoint.com",
            model="gpt-4"
        )
        assert client.endpoint == "https://custom.endpoint.com"
        assert client.model == "gpt-4"
    
    @patch('shared.ai_client.AIClient._get_client')
    def test_generate_recommendation_success(self, mock_get_client):
        """Should parse valid AI response correctly."""
        # Mock the AI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "title": "Easy recovery run",
            "workout": {
                "type": "Running",
                "durationMinutes": 45,
                "details": ["Easy pace for 45 minutes"]
            },
            "rationale": "Recovery after yesterday's hard session.",
            "confidence": "medium"
        })
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        client = AIClient()
        context = {
            "start_date": "2026-01-20",
            "end_date": "2026-02-03",
            "total_activities": 5,
            "total_distance_miles": 25.0,
            "total_duration_minutes": 180,
            "rest_days_count": 3,
            "activity_types": ["Running"]
        }
        
        result = client.generate_recommendation(context)
        
        assert result["title"] == "Easy recovery run"
        assert result["workout"]["type"] == "Running"
        assert result["confidence"] == "medium"
    
    @patch('shared.ai_client.AIClient._get_client')
    def test_generate_recommendation_with_markdown_codeblock(self, mock_get_client):
        """Should handle AI response wrapped in markdown code block."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """```json
{
    "title": "Tempo run",
    "workout": {
        "type": "Running",
        "durationMinutes": 50,
        "details": ["Warm up", "Tempo", "Cool down"]
    },
    "rationale": "Time for speed work.",
    "confidence": "high"
}
```"""
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        client = AIClient()
        result = client.generate_recommendation({"total_activities": 3})
        
        assert result["title"] == "Tempo run"
        assert result["confidence"] == "high"
    
    @patch('shared.ai_client.AIClient._get_client')
    def test_generate_recommendation_invalid_json(self, mock_get_client):
        """Should raise AIClientError for invalid JSON response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is not JSON at all"
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        client = AIClient()
        
        with pytest.raises(AIClientError) as exc_info:
            client.generate_recommendation({"total_activities": 1})
        
        assert "not valid JSON" in str(exc_info.value)
    
    @patch('shared.ai_client.AIClient._get_client')
    def test_generate_recommendation_missing_field(self, mock_get_client):
        """Should raise AIClientError for response missing required fields."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "title": "Easy run",
            # Missing: workout, rationale, confidence
        })
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        client = AIClient()
        
        with pytest.raises(AIClientError) as exc_info:
            client.generate_recommendation({"total_activities": 1})
        
        assert "missing required field" in str(exc_info.value)


class TestCoachSystemPrompt:
    """Tests for the coach system prompt."""
    
    def test_prompt_includes_guidelines(self):
        """System prompt should include training guidelines."""
        assert "Polarized Training" in COACH_SYSTEM_PROMPT
        assert "consecutive days" in COACH_SYSTEM_PROMPT
        assert "long run" in COACH_SYSTEM_PROMPT.lower()
    
    def test_prompt_specifies_json_schema(self):
        """System prompt should specify required JSON schema."""
        assert '"title"' in COACH_SYSTEM_PROMPT
        assert '"workout"' in COACH_SYSTEM_PROMPT
        assert '"rationale"' in COACH_SYSTEM_PROMPT
        assert '"confidence"' in COACH_SYSTEM_PROMPT
    
    def test_prompt_specifies_workout_types(self):
        """System prompt should specify allowed workout types."""
        assert "Running" in COACH_SYSTEM_PROMPT
        assert "Cross-training" in COACH_SYSTEM_PROMPT
        assert "Rest" in COACH_SYSTEM_PROMPT
