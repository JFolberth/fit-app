"""
MCP (Model Context Protocol) client for communicating with the remote Cosmos data server.

Uses Streamable HTTP (SSE) protocol to invoke MCP tools:
- query_cosmos: Query Cosmos DB for activities
- count_document: Count documents matching criteria  
- list_distinct_values: Get distinct values for a field
"""

import json
import logging
import os
import re
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# Default MCP server endpoint (auth environment)
DEFAULT_MCP_ENDPOINT = "https://ca-fitapp-mcp-auth.braveground-fdce88f6.eastus2.azurecontainerapps.io/mcp"

# Timeout for MCP calls (within 3s total budget)
MCP_TIMEOUT_SECONDS = 2.0


class MCPClientError(Exception):
    """Exception raised when MCP server communication fails."""
    pass


class MCPClient:
    """
    Client for communicating with the MCP server via Streamable HTTP.
    
    The MCP server provides tools to query Cosmos DB for activity data.
    """
    
    def __init__(self, endpoint: Optional[str] = None):
        """
        Initialize MCP client.
        
        Args:
            endpoint: MCP server endpoint URL. Defaults to MCP_SERVER_ENDPOINT env var
                     or the default dev endpoint.
        """
        self.endpoint = endpoint or os.environ.get("MCP_SERVER_ENDPOINT", DEFAULT_MCP_ENDPOINT)
        self._session_id: Optional[str] = None
        self._client = httpx.Client(timeout=MCP_TIMEOUT_SECONDS)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def _initialize_session(self) -> None:
        """Initialize MCP session by calling the initialize method."""
        if self._session_id:
            return  # Already initialized
            
        try:
            request_body = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "fit-app-coach",
                        "version": "1.0.0"
                    }
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            
            response = self._client.post(
                self.endpoint,
                json=request_body,
                headers=headers
            )
            response.raise_for_status()
            
            # Store session ID from response header
            self._session_id = response.headers.get("mcp-session-id")
            
            # Parse response (may be SSE or JSON) for validation only; result is not used
            content_type = response.headers.get("content-type", "")
            if "text/event-stream" in content_type:
                # Validate SSE payload; ignore parsed content
                self._parse_sse_response(response.text)
            else:
                try:
                    # Validate JSON payload; ignore parsed content
                    response.json()
                except json.JSONDecodeError:
                    # Ignore invalid JSON; initialization may still succeed based on headers
                    pass
            
            logger.info(f"MCP session initialized: {self._session_id}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize MCP session: {e}")
            raise MCPClientError(f"Failed to initialize MCP session: {e}")
    
    def _parse_sse_response(self, response_text: str) -> Any:
        """
        Parse Server-Sent Events (SSE) response from MCP server.
        
        SSE format:
            event: message
            data: {"jsonrpc": "2.0", "id": 1, "result": {...}}
        
        Args:
            response_text: Raw SSE response text
            
        Returns:
            Parsed JSON result from the SSE data
        """
        result = None
        for line in response_text.strip().split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                # Extract JSON from "data: {...}" line
                json_str = line[5:].strip()
                if json_str:
                    try:
                        result = json.loads(json_str)
                    except json.JSONDecodeError:
                        continue
        return result

    def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call an MCP tool and return the result.
        
        Args:
            tool_name: Name of the MCP tool to invoke
            arguments: Arguments to pass to the tool
            
        Returns:
            The tool result (parsed from JSON)
            
        Raises:
            MCPClientError: If the tool call fails
        """
        try:
            # Initialize session first
            self._initialize_session()
            
            # MCP JSON-RPC request format
            request_body = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            logger.info(f"Calling MCP tool: {tool_name}")
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            if self._session_id:
                headers["Mcp-Session-Id"] = self._session_id
            
            response = self._client.post(
                self.endpoint,
                json=request_body,
                headers=headers
            )
            response.raise_for_status()
            
            # Check content type - MCP server may return SSE or JSON
            content_type = response.headers.get("content-type", "")
            
            if "text/event-stream" in content_type:
                # Parse SSE response
                result = self._parse_sse_response(response.text)
                if result is None:
                    raise MCPClientError("Empty SSE response from MCP server")
            else:
                # Parse JSON response
                result = response.json()
            
            if "error" in result:
                raise MCPClientError(f"MCP tool error: {result['error']}")
            
            # MCP tools/call returns {content: [{type: "text", text: "..."}], ...}
            tool_result = result.get("result", {})
            content = tool_result.get("content", [])
            if content and isinstance(content, list):
                text = content[0].get("text", "")
                return text
            
            # Fallback: return raw result
            return tool_result
            
        except httpx.TimeoutException:
            logger.warning(f"MCP tool {tool_name} timed out after {MCP_TIMEOUT_SECONDS}s")
            raise MCPClientError(f"MCP tool {tool_name} timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"MCP HTTP error: {e.response.status_code}")
            raise MCPClientError(f"MCP HTTP error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"MCP client error: {e}")
            raise MCPClientError(f"MCP client error: {e}")
    
    @staticmethod
    def _parse_documents_text(text: str) -> List[Dict[str, Any]]:
        """
        Parse MCP server's text-formatted document results into dicts.
        
        The MCP server returns results in this format:
            Results:
            --------------------------------------------------
            
            Document 1:
              type: Running
              duration: 60
              distance: 5
              ...
            
            Document 2:
              ...
        
        Args:
            text: Raw text response from MCP query_cosmos tool
            
        Returns:
            List of parsed document dicts
        """
        documents = []
        current_doc: Dict[str, Any] = {}
        
        for line in text.split('\n'):
            # Skip header lines
            if line.startswith('Results:') or line.startswith('---') or not line.strip():
                if current_doc:
                    # Blank line after a doc means it's complete
                    pass
                continue
            
            # New document starts
            doc_match = re.match(r'^Document \d+:', line)
            if doc_match:
                if current_doc:
                    documents.append(current_doc)
                current_doc = {}
                continue
            
            # Parse key: value lines (indented with 2 spaces)
            kv_match = re.match(r'^\s+(\w[\w_]*): (.*)', line)
            if kv_match:
                key = kv_match.group(1)
                value_str = kv_match.group(2).strip()
                
                # Skip Cosmos system fields
                if key.startswith('_'):
                    continue
                
                # Parse value types
                if value_str == 'None' or value_str == '':
                    value = None
                elif value_str.lower() in ('true', 'false'):
                    value = value_str.lower() == 'true'
                else:
                    try:
                        # Try int first, then float
                        if '.' in value_str:
                            value = float(value_str)
                        else:
                            value = int(value_str)
                    except ValueError:
                        value = value_str
                
                current_doc[key] = value
        
        # Don't forget the last document
        if current_doc:
            documents.append(current_doc)
        
        return documents

    def query_activities(
        self,
        start_date: date,
        end_date: date,
        limit: int = 100,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query recent activities from Cosmos DB via MCP.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            limit: Maximum number of activities to return
            user_id: Filter activities to this user (required for per-user isolation)
            
        Returns:
            List of activity documents
        """
        # Build query with user isolation filter
        conditions = [
            f"c.date >= '{start_date.isoformat()}'",
            f"c.date <= '{end_date.isoformat()}'",
        ]
        if user_id:
            conditions.append(f"c.userId = '{user_id}'")
        where_clause = " AND ".join(conditions)
        
        result = self._call_tool("query_cosmos", {
            "query": f"SELECT * FROM c WHERE {where_clause} ORDER BY c.date DESC",
        })
        
        # MCP server returns formatted text, parse into document dicts
        if isinstance(result, str):
            return self._parse_documents_text(result)
        return result.get("documents", [])
    
    def count_activities(self, start_date: date, end_date: date, user_id: Optional[str] = None) -> int:
        """
        Count activities in a date range.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            user_id: Filter to this user (required for per-user isolation)
            
        Returns:
            Number of activities
        """
        conditions = [
            f"c.date >= '{start_date.isoformat()}'",
            f"c.date <= '{end_date.isoformat()}'",
        ]
        if user_id:
            conditions.append(f"c.userId = '{user_id}'")
        where_clause = " AND ".join(conditions)
        
        result = self._call_tool("count_documents", {
            "container_name": "activities"
        })
        
        # MCP server returns text like "Total documents: 15"
        if isinstance(result, str):
            match = re.search(r'(\d+)', result)
            return int(match.group(1)) if match else 0
        return result.get("count", 0)
    
    def get_activity_types(self, start_date: date, end_date: date, user_id: Optional[str] = None) -> List[str]:
        """
        Get distinct activity types in a date range.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            user_id: Filter to this user (required for per-user isolation)
            
        Returns:
            List of distinct activity type strings
        """
        conditions = [
            f"c.date >= '{start_date.isoformat()}'",
            f"c.date <= '{end_date.isoformat()}'",
        ]
        if user_id:
            conditions.append(f"c.userId = '{user_id}'")
        where_clause = " AND ".join(conditions)
        
        result = self._call_tool("list_distinct_values", {
            "field_name": "type",
            "container_name": "activities"
        })
        
        # MCP server returns text like "Distinct values for 'type': Running, Rowing, Rucking"
        if isinstance(result, str):
            # Parse values from text response
            match = re.search(r':\s*(.+)', result)
            if match:
                values = [v.strip() for v in match.group(1).split(',') if v.strip()]
                return values
            return []
        return result.get("values", [])


def get_mcp_client() -> MCPClient:
    """
    Factory function to create an MCP client instance.
    
    Returns:
        Configured MCPClient instance
    """
    return MCPClient()
