"""
Unit tests for MCP client.

Tests MCPClient with mocked HTTP responses and text parsing.
"""

from datetime import date
from unittest.mock import patch

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


class TestParseDocumentsText:
    """Tests for _parse_documents_text static method."""

    def test_parse_multiple_documents(self):
        """Should parse multiple documents from MCP text response."""
        text = """Results:
--------------------------------------------------

Document 1:
  type: Running
  duration: 66.3
  distance: 5
  avgBpm: 153
  comments: tempo run
  date: 2026-02-15
  id: abc-123
  userId: user-1
  _rid: xyz==
  _self: dbs/x/colls/y/docs/z/

Document 2:
  type: Rowing
  duration: 60
  distance: None
  avgBpm: 98
  comments: None
  date: 2026-02-14
  id: def-456
  userId: user-1
  _rid: xyz2==
"""
        docs = MCPClient._parse_documents_text(text)
        assert len(docs) == 2
        assert docs[0]["type"] == "Running"
        assert docs[0]["duration"] == 66.3
        assert docs[0]["distance"] == 5
        assert docs[0]["avgBpm"] == 153
        assert docs[0]["comments"] == "tempo run"
        assert docs[0]["date"] == "2026-02-15"
        assert docs[0]["id"] == "abc-123"
        assert "_rid" not in docs[0]
        assert "_self" not in docs[0]
        assert docs[1]["type"] == "Rowing"
        assert docs[1]["distance"] is None
        assert docs[1]["comments"] is None

    def test_parse_empty_results(self):
        """Should return empty list for no documents."""
        text = "Results:\n--------------------------------------------------\n"
        docs = MCPClient._parse_documents_text(text)
        assert docs == []

    def test_parse_single_document(self):
        """Should parse a single document."""
        text = """Results:
--------------------------------------------------

Document 1:
  type: Rucking
  duration: 45
  distance: 3.5
  date: 2026-02-10
"""
        docs = MCPClient._parse_documents_text(text)
        assert len(docs) == 1
        assert docs[0]["type"] == "Rucking"
        assert docs[0]["duration"] == 45
        assert docs[0]["distance"] == 3.5


class TestMCPClientQueryActivities:
    """Tests for query_activities method."""
    
    @patch.object(MCPClient, '_call_tool')
    def test_query_activities_success_text_format(self, mock_call_tool):
        """Should parse activities from MCP text response."""
        mock_call_tool.return_value = """Results:
--------------------------------------------------

Document 1:
  type: Running
  duration: 60
  distance: 5
  date: 2026-02-01
  id: 1

Document 2:
  type: Running
  duration: 45
  distance: 3
  date: 2026-02-02
  id: 2
"""
        
        client = MCPClient()
        result = client.query_activities(
            start_date=date(2026, 1, 20),
            end_date=date(2026, 2, 3)
        )
        
        assert len(result) == 2
        assert result[0]["type"] == "Running"
        mock_call_tool.assert_called_once()

    @patch.object(MCPClient, '_call_tool')
    def test_query_activities_with_user_id(self, mock_call_tool):
        """Should include userId filter in query."""
        mock_call_tool.return_value = "Results:\n--------------------------------------------------\n"
        
        client = MCPClient()
        client.query_activities(
            start_date=date(2026, 1, 20),
            end_date=date(2026, 2, 3),
            user_id="user-123"
        )
        
        call_args = mock_call_tool.call_args
        query = call_args[0][1]["query"]
        assert "c.userId = 'user-123'" in query
    
    @patch.object(MCPClient, '_call_tool')
    def test_query_activities_empty_result(self, mock_call_tool):
        """Should return empty list when no activities found."""
        mock_call_tool.return_value = "Results:\n--------------------------------------------------\n"
        
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
        """Should return count from text response."""
        mock_call_tool.return_value = "Total documents in 'activities': 15"
        
        client = MCPClient()
        result = client.count_activities(date(2026, 1, 1), date(2026, 2, 3))
        
        assert result == 15
    
    @patch.object(MCPClient, '_call_tool')
    def test_count_activities_zero(self, mock_call_tool):
        """Should return 0 when no activities found."""
        mock_call_tool.return_value = "Total documents in 'activities': 0"
        
        client = MCPClient()
        result = client.count_activities(date(2026, 1, 1), date(2026, 1, 5))
        
        assert result == 0


class TestMCPClientGetActivityTypes:
    """Tests for get_activity_types method."""
    
    @patch.object(MCPClient, '_call_tool')
    def test_get_activity_types_success(self, mock_call_tool):
        """Should return list of activity types from text response."""
        mock_call_tool.return_value = "Distinct values for 'type': Running, Rowing, Rucking"
        
        client = MCPClient()
        result = client.get_activity_types(date(2026, 1, 1), date(2026, 2, 3))
        
        assert len(result) == 3
        assert "Running" in result
        assert "Rowing" in result
    
    @patch.object(MCPClient, '_call_tool')
    def test_get_activity_types_empty(self, mock_call_tool):
        """Should return empty list when no types found."""
        mock_call_tool.return_value = "No distinct values found"
        
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
