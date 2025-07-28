# conftest.py for pytest fixtures
import pytest
import os
import sys
import json

from unittest import mock

from app import app as actual_chalice_app   # Import your Chalice app object
from chalice.local import LocalGateway
from chalice.config import Config as ChaliceConfig

# Ensure app.py is in the Python path for imports
# This should be the path to the directory containing app.py
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(PROJECT_ROOT)

# You might want to set up environment variables or other configurations here
# For example, by loading a .env file if you use one for local dev:
# from dotenv import load_dotenv
# if os.path.exists(os.path.join(PROJECT_ROOT, '.env')):
#     load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
# else:
#     print("Warning: .env file not found, tests might fail if they rely"
#           + " on env vars.")


class MockClientResponse:
    def __init__(self, response_dict):
        self.status_code = response_dict['statusCode']
        # Normalize header keys to lowercase for consistent access
        self.headers = {k.lower(): v for k, v
                        in response_dict.get('headers', {}).items()}
        raw_body_from_gw = response_dict.get('body')
        self._raw_body = raw_body_from_gw \
            if raw_body_from_gw is not None \
            else ''
        self._json_body_loaded = False
        self._json_cache = None

    @property
    def json_body(self):
        if not self._json_body_loaded:
            content_type = self.headers.get('content-type', '').lower()
            print("[DEBUG MockClientResponse] Attempting to parse JSON. "
                  + f"Content-Type: '{content_type}', Raw body (first 200"
                  + f" chars): '{self._raw_body[:200]}'")
            if not self._raw_body:
                print("[DEBUG MockClientResponse] Raw body is empty. "
                      + "json_body will be None.")
                self._json_cache = None
            # Only attempt to parse as JSON if content type suggests it or if
            # it's not explicitly something else
            elif 'application/json' in content_type or not content_type \
                 or content_type == 'text/plain':
                # Attempt parsing for text/plain too, as Chalice might default
                # to it for strings that are actually JSON.
                try:
                    self._json_cache = json.loads(self._raw_body)
                    print("[DEBUG MockClientResponse] Successfully "
                          + "parsed JSON.")
                except json.JSONDecodeError as e:
                    if 'application/json' in content_type:
                        print("[DEBUG MockClientResponse] JSONDecodeError "
                              + f"for application/json: {e}. Raw body (first "
                              + f" 200 chars): '{self._raw_body[:200]}'. "
                              + "json_body will be None.")
                    else:
                        print("[DEBUG MockClientResponse] Content-Type "
                              + f"was '{content_type}'. Attempted JSON "
                              + f"parse failed: {e}. Raw body (first 200 "
                              + f"chars): '{self._raw_body[:200]}'. "
                              + "json_body will be None.")
                    self._json_cache = None
            else:
                print("[DEBUG MockClientResponse] Content-Type "
                      + f"('{content_type}') is not 'application/json' "
                      + "and not attempting parse. json_body will be None.")
                self._json_cache = None
            self._json_body_loaded = True
        return self._json_cache

    @property
    def body(self):    # Raw body as bytes
        return self._raw_body.encode('utf-8')

    @property
    def text(self):    # Raw body as string
        return self._raw_body


class CustomTestClient:
    def __init__(self, chalice_app_obj):
        # Create a minimal ChaliceConfig.
        # try:
        #     # Try to load config from .chalice/config.json if it exists
        #     # This might be necessary if your app uses app.lambda_context for
        #     # stage variables
        #     config_file_path = os.path.join(PROJECT_ROOT, '.chalice',
        #                                     'config.json')
        #     if os.path.exists(config_file_path):
        #         config = ChaliceConfig.load(project_dir=PROJECT_ROOT)
        #     else:
        #         print("Chalice config file (.chalice/config.json) not found,"
        #               + " using default config.")
        #         config = ChaliceConfig()    # Basic default config
        # except Exception as e:
        #     print(f"Error loading Chalice config, using default: {e}")
        #     config = ChaliceConfig()

        config = ChaliceConfig()    # Basic default config

        self.gateway = LocalGateway(chalice_app_obj, config)

    def _request(self, method, path, headers=None, json_data=None, data=None,
                 query_params=None):
        req_headers = headers.copy() if headers is not None else {}
        req_body_str = ''    # LocalGateway expects a string body

        # LocalGateway expects path to include query string if present
        request_path = path
        if query_params:
            from urllib.parse import urlencode
            request_path += '?' + urlencode(query_params)

        if json_data is not None:
            req_body_str = json.dumps(json_data)
            if 'content-type' not in (h.lower() for h in req_headers):
                req_headers['content-type'] = 'application/json'
        elif data is not None:
            # Intended for form data (x-www-form-urlencoded)
            if isinstance(data, dict):
                from urllib.parse import urlencode
                req_body_str = urlencode(data)
                if 'content-type' not in (h.lower() for h in req_headers):
                    req_headers['content-type'] = \
                        'application/x-www-form-urlencoded'
            elif isinstance(data, str):
                req_body_str = data    # Assume pre-encoded string
            else:
                req_body_str = str(data)

        # Ensure all header values are strings, LocalGateway can be picky
        for key, value in req_headers.items():
            if not isinstance(value, str):
                req_headers[key] = str(value)

        response_dict = self.gateway.handle_request(
            method=method,
            path=request_path,    # Use path with query string
            headers=req_headers,
            body=req_body_str
        )
        return MockClientResponse(response_dict)

    def get(self, path, headers=None, params=None):
        # `params` for query parameters
        return self._request('GET', path, headers=headers, query_params=params)

    def post(self, path, headers=None, json=None, data=None, params=None):
        return self._request('POST', path, headers=headers, json_data=json,
                             data=data, query_params=params)

    # Add other HTTP methods (PUT, DELETE, PATCH, etc.) as needed, e.g.:
    # def put(self, path, headers=None, json=None, data=None, params=None):
    #     return self._request('PUT', path, headers=headers, json_data=json,
    #                          data=data, query_params=params)

    # def delete(self, path, headers=None, params=None):
    #     return self._request('DELETE', path, headers=headers,
    #                          query_params=params)


# Helper to create a mock CurrentRequest-like object
def mock_current_request(
    headers=None,
    raw_body=b'',
    json_body=None,
    query_params=None,  # For to_dict()
    method='GET',
    uri_params=None,
    context=None,
    stage_vars=None,
    authorizer_principal_id=None,  # For context['authorizer']['principalId']
    is_xhr=False
):
    request_mock = mock.MagicMock()
    request_mock.headers = headers if headers is not None else {}
    request_mock.raw_body = raw_body
    request_mock.json_body = json_body
    request_mock.method = method
    request_mock.uri_params = uri_params if uri_params is not None else {}
    request_mock.context = context if context is not None else {}
    if authorizer_principal_id:
        if 'authorizer' not in request_mock.context:
            request_mock.context['authorizer'] = {}
        request_mock.context['authorizer']['principalId'] = \
            authorizer_principal_id

    request_mock.stage_vars = stage_vars if stage_vars is not None else {}
    request_mock.is_xhr = is_xhr

    # Mock the to_dict() method, used by get_query_params
    request_mock.to_dict.return_value = {
        'headers': request_mock.headers,
        'uri_params': request_mock.uri_params,
        'method': request_mock.method,
        'context': request_mock.context,
        'stage_vars': request_mock.stage_vars,
        'query_params': query_params if query_params is not None else {}
    }
    return request_mock


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
                "AUTH0_MAPI_API_TOKEN": AUTH0_MAPI_TOKEN,
                "TELEGRAM_CHAT_ID": "test_telegram_chat_id",
                "BANK_PERCENT_INCREASE_OFFICIAL": "0.53",
                "BANK_PERCENT_INCREASE_GOOGLE": "1.00"
            },
            clear=True):
        yield


@pytest.fixture
def mock_requires_auth():
    """Fixture to mock the requires_auth decorator."""
    decoded_payload = {
        'sub': 'mock_user',
        'iss': 'test_jwt_issuer',
        'aud': 'test_api_audience'
    }

    # Set current_request directly on the app instance for
    # the decorator
    mock_req_for_jwt = mock_current_request(
        headers={'Authorization': 'Bearer valid_jwt_token'},
        context={}
    )
    original_current_request = getattr(actual_chalice_app, 'current_request', None)
    # This is the app.current_request the decorator will use
    actual_chalice_app.current_request = mock_req_for_jwt

    with mock.patch('app.get_token_auth_header',
                    return_value='Bearer valid_jwt_token'), \
         mock.patch('app.jwt.decode', return_value=decoded_payload) \
            as mock_decode:
        try:
            yield mock_decode
        finally:
            if original_current_request is not None:
                actual_chalice_app.current_request = original_current_request
            elif hasattr(actual_chalice_app, 'current_request'):   # Check if it was set by us
                del actual_chalice_app.current_request


@pytest.fixture(scope='session')
def chalice_app_instance():
    """Provides the Chalice app instance for testing."""
    # actual_chalice_app is imported from app.py at the top of this file
    return actual_chalice_app


@pytest.fixture
def client(chalice_app_instance):
    """Provides a custom test client for the Chalice app."""
    return CustomTestClient(chalice_app_instance)
