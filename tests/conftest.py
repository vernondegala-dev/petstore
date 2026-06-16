import pytest
from petstore.api_client.client import PetstoreClient

@pytest.fixture(scope="session")
def api_client():
    return PetstoreClient()
