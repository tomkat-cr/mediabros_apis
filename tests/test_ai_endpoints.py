"""
AI endpoints test
"""

from unittest import mock
import pytest

# from tests.conftest import mock_current_request, actual_chalice_app


@pytest.fixture
def mock_openai_api():
    """Fixture to mock the openai_api_with_defaults function."""
    with mock.patch('app.openai_api_with_defaults') as mock_openai_api:
        mock_openai_api.return_value = {'response': 'mocked AI response'}
        yield mock_openai_api


def test_ai_get_endpoint(client, mock_requires_auth, mock_openai_api):
    """Test the /ai GET endpoint."""
    response = client.get('/ai?q=test+query')
    assert response.status_code == 200
    assert response.json_body == {'response': 'mocked AI response'}
    mock_requires_auth.assert_called_once()
    mock_openai_api.assert_called_once()


def test_codex_get_endpoint(client, mock_requires_auth, mock_openai_api):
    """Test the /codex GET endpoint."""
    response = client.get('/codex?q=test+query')
    assert response.status_code == 200
    assert response.json_body == {'response': 'mocked AI response'}
    mock_requires_auth.assert_called_once()
    # Check that the 'm' parameter was correctly added for codex
    mock_openai_api.assert_called_once_with({
        'q': 'test query', 'm': 'code-davinci-002'})
