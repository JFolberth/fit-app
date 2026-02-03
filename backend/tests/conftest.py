import os
import sys
import pytest

# Ensure backend/functions is on sys.path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FUNCTIONS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "functions"))
if FUNCTIONS_DIR not in sys.path:
    sys.path.insert(0, FUNCTIONS_DIR)


# ============================================================================
# Safety: Prevent tests from hitting real Azure services
# ============================================================================

# Environment variables that could trigger real Azure connections
AZURE_ENV_VARS = [
    "COSMOS_ENDPOINT",
    "COSMOS_DATABASE", 
    "COSMOS_ACTIVITIES_CONTAINER",
    "AI_FOUNDRY_ENDPOINT",
    "AI_FOUNDRY_MODEL",
    "MCP_SERVER_ENDPOINT",
]


@pytest.fixture(autouse=True)
def clear_azure_env_vars(monkeypatch):
    """
    Automatically clear Azure environment variables for all tests.
    
    This prevents tests from accidentally connecting to real Azure services
    like Cosmos DB, AI Foundry, or MCP servers. Tests that need these 
    services should use proper mocks or be marked as integration tests
    with RUN_INTEGRATION_TESTS=true.
    """
    for var in AZURE_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def mock_cosmos_env(monkeypatch):
    """
    Fixture for tests that need mock Cosmos environment variables.
    
    Use this when testing code that reads environment variables but
    you want to control the values without hitting real services.
    """
    monkeypatch.setenv("COSMOS_ENDPOINT", "https://mock-cosmos.documents.azure.com:443/")
    monkeypatch.setenv("COSMOS_DATABASE", "mockdb")
    monkeypatch.setenv("COSMOS_ACTIVITIES_CONTAINER", "mockcontainer")


@pytest.fixture
def mock_ai_env(monkeypatch):
    """
    Fixture for tests that need mock AI Foundry environment variables.
    """
    monkeypatch.setenv("AI_FOUNDRY_ENDPOINT", "https://mock-ai.services.ai.azure.com/api/projects/mock")
    monkeypatch.setenv("AI_FOUNDRY_MODEL", "mock-model")


@pytest.fixture
def mock_mcp_env(monkeypatch):
    """
    Fixture for tests that need mock MCP server environment variables.
    """
    monkeypatch.setenv("MCP_SERVER_ENDPOINT", "https://mock-mcp.azurecontainerapps.io/mcp")
