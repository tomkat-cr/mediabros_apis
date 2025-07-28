"""
Login endpoint test
"""
import os
import json

from unittest.mock import patch
from unittest import mock

import pytest


AUTH0_MAPI_TOKEN = 'test_mapi_token_fixture'
AUTH0_DOMAIN_FIXTURE = 'fixture.auth0.com'


@pytest.fixture(autouse=True)
def mock_auth_settings_globally():
    # These are the default settings for most auth tests (JWT path)
    # Patching app.settings ensures that the settings instance
    # used by app.py is modified.

    with mock.patch(
            'chalicelib.utility_jwt.fetch_user_by_entryname',
            return_value={
                'error': False,
                'found': True,
                'resultset': {
                    '_id': 'mock_user_id',
                    'username': 'mock_user',
                    'email': 'mock_email',
                    'full_name': 'mock_full_name',
                    'hashed_password': 'mock_hashed_password',
                    'disabled': False
                }
            },
            create=True), \
        mock.patch('app.settings.SECRET_KEY',
                   'test_jwt_secret_key_fixture', create=True), \
        mock.patch('app.settings.ALGORITHM', 'HS256', create=True), \
        mock.patch.dict(
            # Patches os.environ
            os.environ, {
                "AUTH0_DOMAIN": AUTH0_DOMAIN_FIXTURE,
                "AUTH0_ALGORITHMS": "RS256",
                "AUTH0_API_AUDIENCE": "test_api_audience",
                "AUTH0_MAPI_API_TOKEN": AUTH0_MAPI_TOKEN
            },
            clear=True):
        yield


@pytest.fixture
def mock_auth0_api_call():
    """Fixture to mock the auth0_api_call function."""
    with patch('app.auth0_api_call') as mock:
        mock.return_value = json.dumps({'status': 'ok', 'token': 'mock_token'})
        yield mock


@pytest.fixture
def mock_login_for_access_token():
    """Fixture to mock the login_for_access_token function."""
    with patch('app.login_for_access_token') as mock:
        mock.return_value = {
            'access_token': 'mock_jwt_token',
            'token_type': 'bearer'
        }
        yield mock


@pytest.fixture
def mock_get_multipart_form_data():
    """Fixture to mock get_multipart_form_data."""
    with patch('app.get_multipart_form_data') as mock:
        mock.return_value = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        yield mock


def test_login_endpoint(client, mock_auth0_api_call):
    """Test the /login endpoint."""
    response = client.get('/login')
    assert response.status_code == 200
    assert response.json_body == {'status': 'ok', 'token': 'mock_token'}
    mock_auth0_api_call.assert_called_once()


def test_auth0_client_grant_endpoint(client, mock_auth0_api_call):
    """Test the /auth0_client_grant endpoint."""
    response = client.get('/auth0_client_grant')
    assert response.status_code == 200
    assert response.json_body == {'status': 'ok', 'token': 'mock_token'}
    mock_auth0_api_call.assert_called_once()


def test_token_endpoint(client, mock_get_multipart_form_data,
                        mock_login_for_access_token):
    """Test the /token endpoint."""
    headers = {'Content-Type': 'multipart/form-data; boundary=boundary'}
    # A simple multipart body
    body = (
        b'--boundary\r\n'
        b'Content-Disposition: form-data; name="username"\r\n\r\n'
        b'testuser\r\n'
        b'--boundary\r\n'
        b'Content-Disposition: form-data; name="password"\r\n\r\n'
        b'testpassword\r\n'
        b'--boundary--\r\n'
    )
    response = client.post('/token', headers=headers, data=body)

    assert response.status_code == 200
    assert response.json_body == {
        'access_token': 'mock_jwt_token',
        'token_type': 'bearer'
    }
    mock_get_multipart_form_data.assert_called_once()
    mock_login_for_access_token.assert_called_once()
