import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

mock_table = MagicMock()

with patch('boto3.resource') as mock_boto:
    mock_boto.return_value.Table.return_value = mock_table
    import app as app_module


@pytest.fixture
def client():
    app_module.app.config['TESTING'] = True
    app_module.app.config['SECRET_KEY'] = 'test_secret'
    app_module.users_table = mock_table
    with app_module.app.test_client() as client:
        yield client


@pytest.fixture
def auth_client(client):
    with client.session_transaction() as sess:
        sess['sf_access_token'] = 'mock_sf_token'
    yield client


@pytest.fixture(autouse=True)
def reset_mocks():
    mock_table.reset_mock()
    yield
