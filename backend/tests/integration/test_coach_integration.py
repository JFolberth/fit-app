"""
Integration tests for AI coach feature.

Tests MCP server connectivity, AI agent invocation, and end-to-end recommendation flow.
These tests require access to actual Azure services.
"""

import os
from datetime import date, timedelta

import pytest

# Skip all tests if integration testing is not enabled
pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_INTEGRATION_TESTS", "false").lower() != "true",
    reason="Integration tests disabled. Set RUN_INTEGRATION_TESTS=true to enable."
)


class TestMCPServerConnectivity:
    """Integration tests for MCP server connectivity."""
    
    def test_mcp_server_reachable(self):
        """MCP server should be reachable and respond to health check."""
        from shared.mcp_client import MCPClient, MCPClientError
        
        client = MCPClient()
        try:
            # Try to count activities (should work even with 0 results)
            today = date.today()
            start = today - timedelta(days=14)
            count = client.count_activities(start, today)
            assert isinstance(count, int)
            assert count >= 0
        except MCPClientError as e:
            pytest.fail(f"MCP server not reachable: {e}")
        finally:
            client.close()
    
    def test_query_activities_returns_list(self):
        """Query activities should return a list."""
        from shared.mcp_client import MCPClient
        
        client = MCPClient()
        try:
            today = date.today()
            start = today - timedelta(days=14)
            activities = client.query_activities(start, today, limit=10)
            assert isinstance(activities, list)
        finally:
            client.close()
    
    def test_get_activity_types_returns_list(self):
        """Get activity types should return a list of strings."""
        from shared.mcp_client import MCPClient
        
        client = MCPClient()
        try:
            today = date.today()
            start = today - timedelta(days=14)
            types = client.get_activity_types(start, today)
            assert isinstance(types, list)
            for t in types:
                assert isinstance(t, str)
        finally:
            client.close()


class TestAIAgentInvocation:
    """Integration tests for AI agent invocation."""
    
    def test_ai_agent_generates_recommendation(self):
        """AI agent should generate a valid recommendation."""
        from shared.ai_client import AIClient, AIClientError
        
        client = AIClient()
        try:
            # Provide minimal training context
            context = {
                "start_date": (date.today() - timedelta(days=14)).isoformat(),
                "end_date": date.today().isoformat(),
                "total_activities": 5,
                "total_distance_miles": 25.0,
                "total_duration_minutes": 180,
                "last_hard_workout": (date.today() - timedelta(days=2)).isoformat(),
                "last_long_run": (date.today() - timedelta(days=5)).isoformat(),
                "rest_days_count": 2,
                "activity_types": ["Running"]
            }
            
            result = client.generate_recommendation(context)
            
            # Check required fields
            assert "title" in result
            assert "workout" in result
            assert "rationale" in result
            assert "confidence" in result
            
            # Check workout structure
            assert "type" in result["workout"]
            assert "durationMinutes" in result["workout"]
            assert "details" in result["workout"]
            
        except AIClientError as e:
            pytest.fail(f"AI agent call failed: {e}")
        finally:
            client.close()
    
    def test_ai_response_validates_as_model(self):
        """AI response should validate as DailyRecommendation model."""
        from shared.ai_client import AIClient
        from shared.models import DailyRecommendation, WorkoutDetails
        
        client = AIClient()
        try:
            context = {
                "start_date": (date.today() - timedelta(days=14)).isoformat(),
                "end_date": date.today().isoformat(),
                "total_activities": 3,
                "total_distance_miles": 15.0,
                "total_duration_minutes": 120,
                "rest_days_count": 4,
                "activity_types": ["Running"]
            }
            
            result = client.generate_recommendation(context)
            
            # Should be able to construct valid models
            workout = WorkoutDetails(**result["workout"])
            rec = DailyRecommendation(
                date=date.today(),
                goal="half-marathon",
                title=result["title"],
                workout=workout,
                rationale=result["rationale"],
                confidence=result["confidence"],
                fallback=False
            )
            assert rec.fallback is False
            
        finally:
            client.close()


class TestEndToEndRecommendationFlow:
    """Integration tests for end-to-end recommendation flow."""
    
    def test_full_recommendation_flow(self):
        """Complete flow: MCP query → context build → AI recommendation."""
        from datetime import timedelta
        
        from shared.ai_client import AIClient
        from shared.mcp_client import MCPClient
        from shared.models import DailyRecommendation, TrainingContext, WorkoutDetails
        from shared.training_context import build_training_context
        
        mcp_client = MCPClient()
        ai_client = AIClient()
        
        try:
            # Step 1: Query activities via MCP
            today = date.today()
            start = today - timedelta(days=14)
            activities = mcp_client.query_activities(start, today)
            
            # Step 2: Build training context
            context = build_training_context(activities, start, today)
            assert isinstance(context, TrainingContext)
            
            # Step 3: Generate AI recommendation
            context_dict = context.model_dump(mode="json")
            ai_result = ai_client.generate_recommendation(context_dict)
            
            # Step 4: Validate as DailyRecommendation
            workout = WorkoutDetails(**ai_result["workout"])
            recommendation = DailyRecommendation(
                date=today,
                goal="half-marathon",
                title=ai_result["title"],
                workout=workout,
                rationale=ai_result["rationale"],
                confidence=ai_result["confidence"],
                fallback=False
            )
            
            assert recommendation.date == today
            assert recommendation.fallback is False
            
        finally:
            mcp_client.close()
            ai_client.close()
    
    def test_fallback_on_mcp_failure(self):
        """Should return fallback when MCP server fails."""
        from shared.mcp_client import MCPClient, MCPClientError
        from shared.models import get_fallback_recommendation
        
        # Use invalid endpoint to simulate failure
        client = MCPClient(endpoint="https://invalid.example.com/mcp")
        
        try:
            today = date.today()
            start = today - timedelta(days=14)
            client.query_activities(start, today)
            pytest.fail("Expected MCPClientError")
        except MCPClientError:
            # Expected - use fallback
            fallback = get_fallback_recommendation()
            assert fallback.fallback is True
        finally:
            client.close()
