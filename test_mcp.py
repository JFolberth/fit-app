"""
Quick diagnostic script to test MCP connectivity and data retrieval.
"""

import json
import sys
from datetime import date, timedelta

# Add the functions path for imports
sys.path.insert(0, '/workspaces/fit-app/backend/functions')

from shared.mcp_client import MCPClient, MCPClientError
from shared.training_context import build_training_context

def test_mcp_connection():
    """Test basic MCP connectivity."""
    print("=" * 60)
    print("MCP Client Diagnostic Test")
    print("=" * 60)
    
    # Configuration
    today = date.today()
    start_date = today - timedelta(days=14)
    
    print(f"\nDate range: {start_date} to {today}")
    
    try:
        with MCPClient() as client:
            print(f"\nMCP Endpoint: {client.endpoint}")
            
            # Test 1: Query activities
            print("\n--- Test 1: Query Activities ---")
            try:
                activities = client.query_activities(start_date, today, limit=100)
                print(f"✓ Query successful!")
                print(f"  Activities returned: {len(activities)}")
                
                if activities:
                    print(f"\n  Sample activity:")
                    print(f"  {json.dumps(activities[0], indent=2, default=str)}")
                else:
                    print("  ⚠ No activities returned - database may be empty")
                    
            except MCPClientError as e:
                print(f"✗ Query failed: {e}")
                activities = []
            
            # Test 2: Get activity types
            print("\n--- Test 2: Get Activity Types ---")
            try:
                types = client.get_activity_types(start_date, today)
                print(f"✓ Types successful: {types}")
            except MCPClientError as e:
                print(f"✗ Types failed: {e}")
            
            # Test 3: Build training context (like the coach does)
            print("\n--- Test 3: Build Training Context ---")
            training_context = build_training_context(activities, start_date, today)
            print(f"✓ Training context built:")
            print(f"  Total activities: {training_context.total_activities}")
            print(f"  Total distance: {training_context.total_distance_miles:.1f} miles")
            print(f"  Total duration: {training_context.total_duration_minutes} minutes")
            print(f"  Activity types: {training_context.activity_types}")
            print(f"  Rest days: {training_context.rest_days_count}")
                
    except MCPClientError as e:
        print(f"\n✗ MCP Connection failed: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_connection()
