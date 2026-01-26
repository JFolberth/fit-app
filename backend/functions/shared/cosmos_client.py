import os
from typing import Tuple
from azure.identity import DefaultAzureCredential
from azure.cosmos import CosmosClient

# Environment variables expected (non-secret):
# COSMOS_ENDPOINT, COSMOS_DATABASE, COSMOS_ACTIVITIES_CONTAINER

def get_client() -> CosmosClient:
    endpoint = os.environ.get('COSMOS_ENDPOINT')
    if not endpoint:
        raise RuntimeError('COSMOS_ENDPOINT environment variable must be set')
    credential = DefaultAzureCredential()
    client = CosmosClient(url=endpoint, credential=credential)
    return client


def get_db_and_container(client: CosmosClient) -> Tuple[object, object]:
    db_name = os.environ.get('COSMOS_DATABASE')
    container_name = os.environ.get('COSMOS_ACTIVITIES_CONTAINER')
    if not db_name or not container_name:
        raise RuntimeError('COSMOS_DATABASE and COSMOS_ACTIVITIES_CONTAINER must be set')
    db = client.get_database_client(db_name)
    container = db.get_container_client(container_name)
    return db, container
