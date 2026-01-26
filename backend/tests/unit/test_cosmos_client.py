"""Unit tests for cosmos_client module."""
import os
import pytest
from unittest.mock import patch, MagicMock
from shared.cosmos_client import get_client, get_db_and_container


class TestCosmosClient:
    """Test suite for Cosmos DB client initialization."""

    @patch.dict(os.environ, {"COSMOS_ENDPOINT": "https://test.documents.azure.com:443/"})
    @patch("shared.cosmos_client.DefaultAzureCredential")
    @patch("shared.cosmos_client.CosmosClient")
    def test_get_client_success(self, mock_cosmos_client, mock_credential):
        """get_client() returns CosmosClient with managed identity."""
        mock_cred_instance = MagicMock()
        mock_credential.return_value = mock_cred_instance
        mock_client_instance = MagicMock()
        mock_cosmos_client.return_value = mock_client_instance

        client = get_client()

        mock_credential.assert_called_once()
        mock_cosmos_client.assert_called_once_with(
            url="https://test.documents.azure.com:443/",
            credential=mock_cred_instance
        )
        assert client == mock_client_instance

    @patch.dict(os.environ, {}, clear=True)
    def test_get_client_missing_endpoint(self):
        """get_client() raises RuntimeError if COSMOS_ENDPOINT is missing."""
        with pytest.raises(RuntimeError) as exc:
            get_client()
        assert "COSMOS_ENDPOINT" in str(exc.value)


class TestGetDbAndContainer:
    """Test suite for get_db_and_container function."""

    @patch.dict(
        os.environ,
        {
            "COSMOS_DATABASE": "testdb",
            "COSMOS_ACTIVITIES_CONTAINER": "testcontainer"
        }
    )
    def test_get_db_and_container_success(self):
        """get_db_and_container() returns database and container clients."""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_container = MagicMock()
        
        mock_client.get_database_client.return_value = mock_db
        mock_db.get_container_client.return_value = mock_container

        db, container = get_db_and_container(mock_client)

        mock_client.get_database_client.assert_called_once_with("testdb")
        mock_db.get_container_client.assert_called_once_with("testcontainer")
        assert db == mock_db
        assert container == mock_container

    @patch.dict(os.environ, {"COSMOS_DATABASE": "testdb"}, clear=True)
    def test_get_db_and_container_missing_container(self):
        """get_db_and_container() raises RuntimeError if COSMOS_ACTIVITIES_CONTAINER missing."""
        mock_client = MagicMock()
        with pytest.raises(RuntimeError) as exc:
            get_db_and_container(mock_client)
        assert "COSMOS_ACTIVITIES_CONTAINER" in str(exc.value)

    @patch.dict(os.environ, {"COSMOS_ACTIVITIES_CONTAINER": "testcontainer"}, clear=True)
    def test_get_db_and_container_missing_database(self):
        """get_db_and_container() raises RuntimeError if COSMOS_DATABASE missing."""
        mock_client = MagicMock()
        with pytest.raises(RuntimeError) as exc:
            get_db_and_container(mock_client)
        assert "COSMOS_DATABASE" in str(exc.value)

    @patch.dict(os.environ, {}, clear=True)
    def test_get_db_and_container_missing_both(self):
        """get_db_and_container() raises RuntimeError if both env vars missing."""
        mock_client = MagicMock()
        with pytest.raises(RuntimeError) as exc:
            get_db_and_container(mock_client)
        assert "COSMOS_DATABASE" in str(exc.value) or "COSMOS_ACTIVITIES_CONTAINER" in str(exc.value)
