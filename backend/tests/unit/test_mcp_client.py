"""
Unit tests for MCP client.

Tests MCPClient with mocked HTTP responses.
"""

import json
from datetime import date
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from shared.mcp_client import MCPClient, MCPClientError


class TestMCPClient:
    """Tests for MCPClient class."""
    
    def test_init_with_defaults(self):
        """Should initialize with default endpoint."""
        client = MCPClient()
        assert "ca-fitapp-mcp-dev" in client.endpoint
    
    def test_init_with_custom_endpoint(self):
        """Should accept custom endpoint."""
        client = MCPClient(endpoint="https://custom.mcp.server/mcp")
        assert client.endpoint == "https://custom.mcp.server/mcp"


class TestMCPClientQueryActivities:
    """Tests for query_activities method."""
    
    @patch.object(MCPClient, '_call_tool')
    def test_query_activities_success(self, mock_call_tool):
        """Should return activities from successful query."""
        mock_call_tool.return_value = {
            "documents": [
                {"id": "1", "type": "Running", "date": "2026-02-01"},
                {"id": "2", "type": "Running", "date": "2026-02-02"},
            ]
        }
        
        client = MCPClient()
        result = client.query_activities(
            start_date=date(2026, 1, 20),
            end_date=date(2026, 2, 3)
        )
        
        assert len(result) == 2
        assert result[0]["type"] == "Running"
        mock_call_tool.assert_called_once()
    
    @patch.object(MCPClient, '_call_tool')
    def test_query_activities_empty_result(self, mock_call_tool):
        """Should return empty list when no activities found."""
        mock_call_tool.return_value = {"documents": []}
        
        client = MCPClient()
        result = client.query_activities(date(2026, 1, 1), date(2026, 1, 15))
        
        assert result == []
    
    @patch.object(MCPClient, '_call_tool')
    def test_query_activities_server_error(self, mock_call_tool):
        """Should raise MCPClientError on server error."""
        mock_call_tool.side_effect = MCPClientError("Server error: 500")
        
        client = MCPClient()
        
        with pytest.raises(MCPClientError) as exc_info:
            client.query_activities(date(2026, 1, 1), date(2026, 1, 15))
        
        assert "500" in str(exc_info.value)


class TestMCPClientCountActivities:
    """Tests for count_activities method."""
    
    @patch.object(MCPClient, '_call_tool')
    def test_count_activities_success(self, mock_call_tool):
        """Should return count from successful query."""
        mock_call_tool.return_value = {"count": 15}
        
        client = MCPClient()
        result = client.count_activities(date(2026, 1, 1), date(2026, 2, 3))
        
        assert result == 15
    
    @patch.object(MCPClient, '_call_tool')
    def test_count_activities_zero(self, mock_call_tool):
        """Should return 0 when no activities found."""
        mock_call_tool.return_value = {"count": 0}
        
        client = MCPClient()
        result = client.count_activities(date(2026, 1, 1), date(2026, 1, 5))
        
        assert result == 0


class TestMCPClientGetActivityTypes:
    """Tests for get_activity_types method."""
    
    @patch.object(MCPClient, '_call_tool')
    def test_get_activity_types_success(self, mock_call_tool):
        """Should return list of activity types."""
        mock_call_tool.return_value = {"values": ["Running", "Cross-training", "Strength"]}
        
        client = MCPClient()
        result = client.get_activity_types(date(2026, 1, 1), date(2026, 2, 3))
        
        assert len(result) == 3
        assert "Running" in result
    
    @patch.object(MCPClient, '_call_tool')
    def test_get_activity_types_empty(self, mock_call_tool):
        """Should return empty list when no types found."""
        mock_call_tool.return_value = {"values": []}
        
        client = MCPClient()
        result = client.get_activity_types(date(2026, 1, 1), date(2026, 1, 15))
        
        assert result == []


class TestMCPClientTimeout:
    """Tests for timeout handling."""
    
    @patch.object(MCPClient, '_call_tool')
    def test_timeout_raises_error(self, mock_call_tool):
        """Should raise MCPClientError on timeout."""
        mock_call_tool.side_effect = MCPClientError("Request timed out")
        
        client = MCPClient()
        
        with pytest.raises(MCPClientError) as exc_info:
            client.query_activities(date(2026, 1, 1), date(2026, 2, 3))
        
        assert "timed out" in str(exc_info.value).lower()
