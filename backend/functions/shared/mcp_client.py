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
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

# Default MCP server endpoint (dev environment)
DEFAULT_MCP_ENDPOINT = "https://ca-fitapp-mcp-dev.nicemeadow-fd871464.eastus2.azurecontainerapps.io/mcp"

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
            
            return result.get("result", {})
            
        except httpx.TimeoutException:
            logger.warning(f"MCP tool {tool_name} timed out after {MCP_TIMEOUT_SECONDS}s")
            raise MCPClientError(f"MCP tool {tool_name} timed out")
        except httpx.HTTPStatusError as e:
            logger.error(f"MCP HTTP error: {e.response.status_code}")
            raise MCPClientError(f"MCP HTTP error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"MCP client error: {e}")
            raise MCPClientError(f"MCP client error: {e}")
    
    def query_activities(
        self,
        start_date: date,
        end_date: date,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query recent activities from Cosmos DB via MCP.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            limit: Maximum number of activities to return
            
        Returns:
            List of activity documents
        """
        result = self._call_tool("query_cosmos", {
            "query": f"SELECT * FROM c WHERE c.date >= '{start_date.isoformat()}' AND c.date <= '{end_date.isoformat()}' ORDER BY c.date DESC",
            "limit": limit
        })
        
        return result.get("documents", [])
    
    def count_activities(self, start_date: date, end_date: date) -> int:
        """
        Count activities in a date range.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            
        Returns:
            Number of activities
        """
        result = self._call_tool("count_document", {
            "query": f"SELECT VALUE COUNT(1) FROM c WHERE c.date >= '{start_date.isoformat()}' AND c.date <= '{end_date.isoformat()}'"
        })
        
        return result.get("count", 0)
    
    def get_activity_types(self, start_date: date, end_date: date) -> List[str]:
        """
        Get distinct activity types in a date range.
        
        Args:
            start_date: Start of date range (inclusive)
            end_date: End of date range (inclusive)
            
        Returns:
            List of distinct activity type strings
        """
        result = self._call_tool("list_distinct_values", {
            "field": "type",
            "query": f"c.date >= '{start_date.isoformat()}' AND c.date <= '{end_date.isoformat()}'"
        })
        
        return result.get("values", [])


def get_mcp_client() -> MCPClient:
    """
    Factory function to create an MCP client instance.
    
    Returns:
        Configured MCPClient instance
    """
    return MCPClient()
