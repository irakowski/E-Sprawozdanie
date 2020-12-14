import pytest
from django.test import Client

@pytest.fixture
def client():
    """
    Returns client used in tests
    """
    client = Client()
    return client