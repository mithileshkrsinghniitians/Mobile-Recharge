import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock DynamoDB before importing app
mock_table = MagicMock()

with patch('boto3.resource') as mock_boto:
    mock_boto.return_value.Table.return_value = mock_table
    import app as app_module


@pytest.fixture
def client():
    """Unauthenticated Flask test client."""
    app_module.app.config['TESTING'] = True
    app_module.app.config['SECRET_KEY'] = 'test_secret'
    app_module.users_table = mock_table
    with app_module.app.test_client() as client:
        yield client


@pytest.fixture
def auth_client(client):
    """Authenticated Flask test client (admin session)."""
    with client.session_transaction() as sess:
        sess['sf_access_token'] = 'mock_sf_token'
    yield client


@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset all mock call history before each test."""
    mock_table.reset_mock()
    yield
