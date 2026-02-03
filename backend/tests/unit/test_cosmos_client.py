"""Unit tests for cosmos_client module."""
import os
import pytest
from unittest.mock import patch, MagicMock
from shared.cosmos_client import get_client, get_db_and_container


class TestCosmosClient:
    """Test suite for Cosmos DB client initialization."""

    def test_get_client_success(self, mock_cosmos_env):
        """get_client() returns CosmosClient with managed identity."""
        with patch("shared.cosmos_client.DefaultAzureCredential") as mock_credential, \
             patch("shared.cosmos_client.CosmosClient") as mock_cosmos_client:
            mock_cred_instance = MagicMock()
            mock_credential.return_value = mock_cred_instance
            mock_client_instance = MagicMock()
            mock_cosmos_client.return_value = mock_client_instance

            client = get_client()

            mock_credential.assert_called_once()
            mock_cosmos_client.assert_called_once_with(
                url="https://mock-cosmos.documents.azure.com:443/",
                credential=mock_cred_instance
            )
            assert client == mock_client_instance

    def test_get_client_missing_endpoint(self):
        """get_client() raises RuntimeError if COSMOS_ENDPOINT is missing."""
        # autouse fixture already clears env vars
        with pytest.raises(RuntimeError) as exc:
            get_client()
        assert "COSMOS_ENDPOINT" in str(exc.value)


class TestGetDbAndContainer:
    """Test suite for get_db_and_container function."""

    def test_get_db_and_container_success(self, mock_cosmos_env):
        """get_db_and_container() returns database and container clients."""
        mock_client = MagicMock()
        mock_db = MagicMock()
        mock_container = MagicMock()
        
        mock_client.get_database_client.return_value = mock_db
        mock_db.get_container_client.return_value = mock_container

        db, container = get_db_and_container(mock_client)

        mock_client.get_database_client.assert_called_once_with("mockdb")
        mock_db.get_container_client.assert_called_once_with("mockcontainer")
        assert db == mock_db
        assert container == mock_container

    def test_get_db_and_container_missing_container(self, monkeypatch):
        """get_db_and_container() raises RuntimeError if COSMOS_ACTIVITIES_CONTAINER missing."""
        monkeypatch.setenv("COSMOS_DATABASE", "testdb")
        # COSMOS_ACTIVITIES_CONTAINER is cleared by autouse fixture
        mock_client = MagicMock()
        with pytest.raises(RuntimeError) as exc:
            get_db_and_container(mock_client)
        assert "COSMOS_ACTIVITIES_CONTAINER" in str(exc.value)

    def test_get_db_and_container_missing_database(self, monkeypatch):
        """get_db_and_container() raises RuntimeError if COSMOS_DATABASE missing."""
        monkeypatch.setenv("COSMOS_ACTIVITIES_CONTAINER", "testcontainer")
        # COSMOS_DATABASE is cleared by autouse fixture
        mock_client = MagicMock()
        with pytest.raises(RuntimeError) as exc:
            get_db_and_container(mock_client)
        assert "COSMOS_DATABASE" in str(exc.value)

    def test_get_db_and_container_missing_both(self):
        """get_db_and_container() raises RuntimeError if both env vars missing."""
        # Both vars are cleared by autouse fixture
        mock_client = MagicMock()
        with pytest.raises(RuntimeError) as exc:
            get_db_and_container(mock_client)
        assert "COSMOS_DATABASE" in str(exc.value) or "COSMOS_ACTIVITIES_CONTAINER" in str(exc.value)
