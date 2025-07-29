# app.py
# Chalice implementation for project: mediabros_apis
# 2023-02-04 | CR
#
import email

import logging
from typing import Union
from urllib.request import urlopen
import json
from os import environ as env
from functools import wraps
import http.client

from chalice import Chalice, Response
import boto3
from jose import jwt
from fastapi import HTTPException

from pydantic import BaseModel

from chalicelib.settings import settings
from chalicelib.utility_password import get_password_hash
from chalicelib.utility_jwt import login_for_access_token, \
    get_current_active_user_chalice
from chalicelib.utility_date import get_formatted_date
from chalicelib.utility_general import log_endpoint_debug, \
    log_debug, log_normal
from chalicelib.api_openai import openai_api_with_defaults
from chalicelib.api_currency_exchange import (
    crypto, usdcop, usdveb, veb_cop, usdveb_full, usdveb_monitor)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


app = Chalice(app_name='chalicelib', debug=settings.DEBUG)
app.secret_key = settings.SECRET_KEY
log_normal(f'Mediabros APIs started [AWS Lambda]. {get_formatted_date()}')


# ---------- General use functions ----------


def error_msg_formatter(e, error_code):
    return 'ERROR: ' + str(e) + ' ['+error_code+']'


def jsonify(*args, **kwargs):
    """The jsonify() function in flask returns a flask.Response()
    object that already has the appropriate content-type header
    'application/json' for use with json responses.
    Whereas, the json.dumps() method will just return an encoded
    string, which would require manually adding the MIME type header.
    Reference:
    https://stackoverflow.com/questions/7907596/json-dumps-vs-flask-jsonify
    """
    headers = kwargs.pop('headers', {})
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'

    # Extract status_code if passed, default to 200
    status_code = kwargs.pop('status_code', 200)

    return Response(
        body=json.dumps(
            dict(*args, **kwargs),
            indent=None if app.current_request.is_xhr else 2
        ),
        headers=headers,
        status_code=status_code
    )


def _get_parts():
    """Get the form's input fields for multipart/form-data.
    Reference: https://github.com/aws/chalice/issues/796
    """
    content_type = app.current_request.headers.get('content-type', '')
    if not content_type.startswith('multipart/form-data'):
        return {}

    boundary_array = content_type.split('boundary=')
    if len(boundary_array) != 2:
        raise Exception('No boundary found in content-type header [1]')

    boundary = boundary_array[1]
    if not boundary:
        raise Exception('No boundary found in content-type header [2]')

    body = app.current_request.raw_body
    if not isinstance(body, bytes):
        if isinstance(body, str):
            body = body.encode('utf-8')  # Convert string to bytes
        else:
            raise TypeError("raw_body must be bytes or string")

    data = email.parser.BytesParser().parsebytes(body)

    # Get the email message from the raw body separating the boundaries
    # Reference: https://docs.python.org/3/library/email.parser.html

    parsed = {}
    for part in data.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        name = part.get_param('name', header='content-disposition')
        if name:
            payload = part.get_payload(decode=True)
            if name in parsed:
                parsed[name].append(payload)
            else:
                parsed[name] = [payload]
    return parsed


def get_multipart_form_data():
    form_data = _get_parts()
    return {k: v[0] for (k, v) in form_data.items()}


def get_form_data():
    form_data = app.current_request.json_body
    if form_data is None:
        form_data = dict()
    return form_data


def get_query_params():
    query_params = app.current_request.to_dict()['query_params']
    if query_params is None:
        query_params = dict()
    return query_params


def http_response(status_code, detail, headers):
    """This is the way to emulate Flask's make_response()
    but using chalice.Response(), and return a
    HTTPResponse with status different than 200, without
    a 'raise' and therefore a HTTP error 500...
    """
    # Ensure headers is a dict
    final_headers = headers.copy() if headers is not None else {}
    if 'Content-Type' not in final_headers:
        final_headers['Content-Type'] = 'application/json'

    return Response(
        body={
            'code': status_code,
            'detail': detail
        },
        headers=final_headers,
        status_code=status_code
    )


# ---------- OAUTH0 for the API ----------


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def handle_auth_error(ex):
    return jsonify(ex.error, status_code=ex.status_code)


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    request = app.current_request
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                         "description":
                         "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must start with"
                         " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                         "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                         "description":
                         "Authorization header must be"
                         " Bearer token"}, 401)

    token = parts[1]
    return token


def requires_auth(f):
    """Wrapper to determine if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if settings.JWT_ENABLED == "1":
            return jwt_decorated(*args, **kwargs)
        if settings.AUTH0_ENABLED == "1":
            return auth_decorated(*args, **kwargs)
        return f(*args, **kwargs)

    def jwt_decorated(*args, **kwargs):
        try:
            token = get_token_auth_header()
            log_debug(f'>> requires_auth.jwt_decorated | token: {token}')
            jwt_response = get_current_active_user_chalice(token)
            log_debug('>> requires_auth.jwt_decorated | jwt_response:' +
                      f' {jwt_response}')
        except Exception as e:
            return http_response(
                e.status_code or 500,
                error_msg_formatter(e, 'JWT_AUTH_ERROR'),
                {'Content-Type': 'application/json'}
            )
        if isinstance(jwt_response, HTTPException):
            return http_response(
                jwt_response.status_code,
                jwt_response.detail,
                jwt_response.headers
            )
        if isinstance(jwt_response, Exception):
            raise jwt_response
        app.current_request.context.update({'user': jwt_response.model_dump()})
        return f(*args, **kwargs)

    def auth_decorated(*args, **kwargs):
        try:
            token = get_token_auth_header()
            log_debug(f'get_token_auth_header | token: {token}')
        except Exception as e:
            return http_response(
                e.status_code or 500,
                error_msg_formatter(e, 'JWT_AUTH_ERROR'),
                {'Content-Type': 'application/json'}
            )
        url = "https://"+env.get("AUTH0_DOMAIN")+"/.well-known/jwks.json"
        log_debug(f'auth_decorated | url: {url}')
        try:
            jsonurl = urlopen(url)
            log_debug(f'auth_decorated | jsonurl: {jsonurl}')
        except Exception as e:
            raise AuthError({"code": "invalid_claims",
                             "description": "Unable to fetch JWKS"
                             " (" + str(e) + ")"}, 401)
        try:
            jwks = json.loads(jsonurl.read())
            log_debug(f'auth_decorated | jwks: {jwks}')
        except Exception as e:
            raise AuthError({"code": "invalid_claims",
                             "description": "Unable to parse JWKS"
                             " (" + str(e) + ")"}, 401)
        unverified_header = jwt.get_unverified_header(token)
        log_debug(f'auth_decorated | unverified_header: {unverified_header}')
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            log_debug(f'auth_decorated | rsa_key: {rsa_key}')
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=[env.get("AUTH0_ALGORITHMS")],
                    audience=env.get("AUTH0_API_AUDIENCE"),
                    issuer="https://"+env.get("AUTH0_DOMAIN")+"/"
                )
                log_debug(f'auth_decorated | payload: {payload}')
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                 "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                 "description":
                                 "incorrect claims,"
                                 "please check the audience and issuer"}, 401)
            except Exception as e:
                raise AuthError({"code": "invalid_header",
                                 "description":
                                 "Unable to parse authentication"
                                 " token: " + str(e)}, 401)

            app.current_request.context.update({'current_user': payload})
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                         "description": "Unable to find appropriate key"}, 401)
    return decorated


def auth0_api_call(endpoint_suffix, body_data, additional_headers={}):
    """Auth0 API/MAPI call
    """
    body = json.dumps(body_data)
    conn = http.client.HTTPSConnection(env.get("AUTH0_DOMAIN"))
    headers = {'content-type': "application/json"} | additional_headers

    conn.request("POST", endpoint_suffix, body, headers)

    res = conn.getresponse()
    data = res.read()
    return (data.decode("utf-8"))


# ---------- DynamoDB generals ----------


def get_app_db(table_name):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    return table


# ---------- Chalice app ----------


# OAUTH0 endpoints


@app.route('/login', methods=['GET'])
def login():
    """Login
    """
    body_data = {
        "client_id": env.get("AUTH0_MAPI_CLIENT_ID"),
        "client_secret": env.get("AUTH0_MAPI_CLIENT_SECRET"),
        "audience": "https://" + env.get("AUTH0_DOMAIN") + "/api/v2/",
        "grant_type": "client_credentials"
    }
    return auth0_api_call("/oauth/token", body_data)


@app.route('/auth0_client_grant', methods=['GET'])
def auth0_client_grant():
    """MAPI call to create client_grants and allow to get client_credentials
    """
    body_data = {
        "client_id": env.get("AUTH0_MAPI_CLIENT_ID"),
        "audience": "https://" + env.get("AUTH0_DOMAIN") + "/api/v2/",
        "scope": ["create:client_grants"],
    }
    additional_headers = {
        "Authorization": "Bearer " + env.get("AUTH0_MAPI_API_TOKEN")
    }
    return auth0_api_call(
        "/api/v2/client-grants", body_data, additional_headers
    )


# JWT Authentication EndPoints


class UserData(BaseModel):
    username: str
    password: str


@app.route("/token", methods=['POST'],
           content_types=['multipart/form-data'])
def login_for_access_token_endpoint():
    log_endpoint_debug('/token')
    log_debug('login_for_access_token_endpoint | Before get form_data!')
    form_data = get_multipart_form_data()
    log_debug(f'login_for_access_token_endpoint | form_data: {form_data}')
    user_data = UserData(
        username=form_data.get('username'),
        password=form_data.get('password'),
    )
    try:
        login_data = login_for_access_token(user_data)
    except HTTPException as err:
        return http_response(
            err.status_code,
            err.detail,
            err.headers
        )
    except Exception as err:
        raise err
    else:
        # I cannot return Token() class because all chalice
        # responses must be serializable, like dict() or chalice.Response()
        #
        # return Token(
        #     access_token=login_data.get('access_token'),
        #     token_type=login_data.get('token_type'),
        # )
        return login_data


@app.route("/pget", methods=['GET'])
def pget():
    log_endpoint_debug('/pget')
    query_params = get_query_params()
    log_debug(f'pget | query_params: {query_params}')
    password = query_params['p']
    return dict(
        {
            'password_hashed': get_password_hash(password)
        }
    )


# This API specific EndPoints


class Body(BaseModel):
    q: Union[str, None] = None
    debug: Union[int, None] = None
    p: Union[str, None] = None
    m: Union[str, None] = None
    t: Union[str, None] = None
    mt: Union[str, None] = None


@app.route("/query_params", methods=['GET'])
def api_query_params():
    log_endpoint_debug('/query_params')
    api_response = app.current_request.to_dict()
    log_debug(api_response)
    return api_response


# @app.route("/get_cnf", methods=['GET'])
# def api_get_cnf():
#     log_endpoint_debug('/get_cnf')
#     api_response = {
#         'DEBUG': settings.DEBUG,
#         'APP_NAME': settings.APP_NAME,
#         'TELEGRAM_BOT_TOKEN': settings.TELEGRAM_BOT_TOKEN,
#         'TELEGRAM_CHAT_ID': settings.TELEGRAM_CHAT_ID,
#         'SERVER_NAME': settings.SERVER_NAME,
#         'OPENAI_API_KEY': settings.OPENAI_API_KEY,
#         'DB_URI': settings.DB_URI,
#         'DB_NAME': settings.DB_NAME,
#         'SECRET_KEY': settings.SECRET_KEY,
#         'ALGORITHM': settings.ALGORITHM,
#         'ACCESS_TOKEN_EXPIRE_MINUTES': settings.ACCESS_TOKEN_EXPIRE_MINUTES,
#     }
#     log_debug(api_response)
#     return api_response


@app.route("/ai", methods=['POST'])
@requires_auth
def ai_post():
    log_endpoint_debug('/ai POST')
    form_data = get_form_data()
    log_debug(f'ai_post: body = {str(form_data)}')
    api_response = openai_api_with_defaults(form_data)
    log_debug(f'ai_post: api_response = {api_response}')
    return api_response


@app.route("/ai", methods=['GET'])
@requires_auth
def ai_get():
    log_endpoint_debug('/ai GET')
    query_params = get_query_params()
    log_debug(f'ai_get: request = {query_params}')
    api_response = openai_api_with_defaults(query_params)
    log_debug(f'ai_get: api_response = {api_response}')
    return api_response


@app.route("/codex", methods=['GET'])
@requires_auth
def codex_get():
    log_endpoint_debug('/codex')
    request_params = get_query_params()
    request_params['m'] = 'code-davinci-002'
    log_debug(f'codex_get: request = {request_params}')
    api_response = openai_api_with_defaults(request_params)
    log_debug(f'codex_get: api_response = {api_response}')
    return api_response


@app.route("/usdcop", methods=['GET'])
def endpoint_usdcop_plain():
    log_endpoint_debug('/usdcop')
    return usdcop(False)


@app.route("/usdcop/{debug}", methods=['GET'])
def endpoint_usdcop(debug: int):
    log_endpoint_debug(f'/usdcop/{debug}')
    return usdcop(str(debug) == "1")


@app.route("/usdveb", methods=['GET'])
def endpoint_usdveb_plain():
    log_endpoint_debug('/usdveb')
    return usdveb(False)


@app.route("/usdveb/{debug}", methods=['GET'])
def endpoint_usdveb(debug: int):
    log_endpoint_debug(f'/usdveb/{debug}')
    return usdveb(str(debug) == "1")


@app.route("/usdveb_full", methods=['GET'])
def endpoint_usdveb_full_plain():
    log_endpoint_debug('/usdveb_full')
    return usdveb_full(False)


@app.route("/usdveb_full/{debug}", methods=['GET'])
def endpoint_usdveb_full(debug: int):
    log_endpoint_debug(f'/usdveb_full/{debug}')
    return usdveb_full(str(debug) == "1")


@app.route("/usdveb_monitor", methods=['GET'])
def endpoint_usdveb_monitor_plain():
    log_endpoint_debug('/usdveb_monitor')
    return usdveb_monitor(False)


@app.route("/usdveb_monitor/{debug}", methods=['GET'])
def endpoint_usdveb_monitor(debug: int):
    log_endpoint_debug(f'/usdveb_monitor/{debug}')
    return usdveb_monitor(str(debug) == "1")


@app.route("/copveb", methods=['GET'])
def endpoint_copveb_plain():
    log_endpoint_debug('/copveb')
    return veb_cop('copveb', False)


@app.route("/copveb/{debug}")
def endpoint_copveb(debug: int):
    log_endpoint_debug(f'/copveb/{debug}')
    return veb_cop('copveb', str(debug) == "1")


@app.route("/vebcop", methods=['GET'])
def endpoint_vebcop_plain():
    log_endpoint_debug('/vebcop')
    return veb_cop('vebcop', False)


@app.route("/vebcop/{debug}", methods=['GET'])
def endpoint_vebcop(debug: int):
    log_endpoint_debug(f'/vebcop/{debug}')
    return veb_cop('vebcop', str(debug) == "1")


@app.route("/btc", methods=['GET'])
def endpoint_btc_plain():
    log_endpoint_debug('/btc')
    return crypto('btc', 'usd', False)


@app.route("/btc/{debug}", methods=['GET'])
def endpoint_btc(debug: int):
    log_endpoint_debug(f'/btc/{debug}')
    return crypto('btc', 'usd', str(debug) == "1")


@app.route("/eth", methods=['GET'])
def endpoint_eth_plain():
    log_endpoint_debug('/eth')
    return crypto('eth', 'usd', False)


@app.route("/eth/{debug}", methods=['GET'])
def endpoint_eth(debug: int):
    log_endpoint_debug(f'/eth/{debug}')
    return crypto('eth', 'usd', str(debug) == "1")


@app.route("/crypto/{symbol}", methods=['GET'])
def endpoint_crypto_plain(symbol: str):
    log_endpoint_debug(f'/crypto/{symbol}')
    return crypto(symbol, 'usd', False)


@app.route("/crypto/{symbol}/{debug}", methods=['GET'])
def endpoint_crypto(symbol: str, debug: int):
    log_endpoint_debug(f'/crypto/{symbol}/{debug}')
    return crypto(symbol, 'usd', str(debug) == "1")


@app.route("/crypto_wc/{symbol}/{currency}/{debug}")
def endpoint_crypto_curr(symbol: str, currency: str, debug: int):
    log_endpoint_debug(f'/crypto_wc/{symbol}/{currency}/{debug}')
    return crypto(symbol, currency, str(debug) == "1")
