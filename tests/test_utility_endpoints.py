"""
Utility endpoints test
"""

from unittest.mock import patch
import pytest

from chalicelib.utility_password import check_password_hash


@pytest.fixture
def mock_get_query_params():
    """Fixture to mock get_query_params to control test input."""
    with patch('app.get_query_params') as mock:
        # Simulate a request with q=test and p=5
        mock.return_value = {'q': 'test', 'p': '5'}
        yield mock


def test_pget_endpoint(client, mock_get_query_params):
    """Test the /pget endpoint.

    This test validates that the /pget endpoint correctly retrieves
    and returns the value of a specific query parameter ('p').
    """
    response = client.get('/pget?q=test&p=5')
    assert response.status_code == 200
    # The endpoint should return the value of 'p'
    assert check_password_hash(response.json_body['password_hashed'], '5')
    mock_get_query_params.assert_called_once()


def test_query_params_endpoint_not_authenticated(client,
                                                 mock_get_query_params):
    """Test the /query_params endpoint.

    This test validates that the /query_params endpoint returns
    the entire dictionary of query parameters from the request.
    """
    response = client.get('/query_params?q=test&p=5')
    print(f'>>> response.json_body: {response.json_body}')
    assert response.status_code == 200
    assert response.json_body == {
        'query_params': {
            'q': 'test',
            'p': '5'
        },
        'headers': {},
        'uri_params': {},
        'method': 'GET',
        'context': {
            'httpMethod': 'GET',
            'resourcePath': '/query_params',
            'identity': {
                'sourceIp': '127.0.0.1'
            },
            'path': '/query_params'
        },
        'stage_vars': {},
        'path': '/query_params'
    }
