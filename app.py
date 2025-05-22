# app.py
# Chalice implementation for project: mediabros_apis
# 2023-02-04 | CR
#
import cgi
from io import BytesIO
import logging
from typing import Union
from urllib.request import urlopen
import json
from os import environ as env
from functools import wraps
import http.client

from chalice import Chalice, Response
import boto3
# from boto3.dynamodb.conditions import Key
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
from chalicelib.api_currency_exchange import crypto, usdcop, usdveb, veb_cop


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


app = Chalice(app_name='chalicelib', debug=settings.DEBUG)
app.secret_key = settings.SECRET_KEY
log_normal(f'Mediabros APIs started [AWS Lambda]. {get_formatted_date()}')


# ---------- General use functions ----------


def error_msg_formatter(e, error_code):
    return 'ERROR: '+str(e) + ' ['+error_code+']'


def jsonify(*args, **kwargs):
    """The jsonify() function in flask returns a flask.Response()
    object that already has the appropriate content-type header
    'application/json' for use with json responses.
    Whereas, the json.dumps() method will just return an encoded
    string, which would require manually adding the MIME type header.
    Reference:
    https://stackoverflow.com/questions/7907596/json-dumps-vs-flask-jsonify
    """
    return app.response_class(
        json.dumps(
            dict(*args, **kwargs),
            indent=None if app.current_request.is_xhr else 2
        ),
        mimetype='application/json'
    )


def _get_parts():
    """This allows to get the form's input fields
    for a multipart/form_data.
    Reference: https://github.com/aws/chalice/issues/796
    """
    rfile = BytesIO(app.current_request.raw_body)
    content_type = app.current_request.headers['content-type']
    _, parameters = cgi.parse_header(content_type)
    parameters['boundary'] = parameters['boundary'].encode('utf-8')
    parsed = cgi.parse_multipart(rfile, parameters)
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
    return Response(
        body={
            "code": status_code,
            "detail": detail,
        },
        status_code=status_code,
        headers=headers
    )


# ---------- OAUTH0 for the API ----------


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


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
        token = get_token_auth_header()
        jwt_response = get_current_active_user_chalice(token)
        if isinstance(jwt_response, HTTPException):
            return http_response(
                jwt_response.status_code,
                jwt_response.detail,
                jwt_response.headers
            )
        if isinstance(jwt_response, Exception):
            raise jwt_response
        return f(*args, **kwargs)

    def auth_decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen(
            "https://"+env.get("AUTH0_DOMAIN")+"/.well-known/jwks.json"
        )
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        log_debug('jwks', jwks)
        log_debug('unverified_header', unverified_header)
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
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=[env.get("AUTH0_ALGORITHMS")],
                    audience=env.get("AUTH0_API_AUDIENCE"),
                    issuer="https://"+env.get("AUTH0_DOMAIN")+"/"
                )
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

            app.current_request.context.update(payload)
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
    log_debug('antes de tomar form_data!')
    form_data = get_multipart_form_data()
    log_debug(f'form_data: {form_data}')
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
    log_debug(f'query_params: {query_params}')
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
    return usdcop(debug == "1")


@app.route("/usdvef", methods=['GET'])
def endpoint_usdvef_plain():
    log_endpoint_debug('/usdvef')
    return usdveb(False)


@app.route("/usdvef/{debug}", methods=['GET'])
def endpoint_usdvef(debug: int):
    log_endpoint_debug(f'/usdvef/{debug}')
    return usdveb(debug == "1")


@app.route("/copveb", methods=['GET'])
def endpoint_copveb_plain():
    log_endpoint_debug('/copveb')
    return veb_cop('copveb', False)


@app.route("/copveb/{debug}")
def endpoint_copveb(debug: int):
    log_endpoint_debug(f'/copveb/{debug}')
    return veb_cop('copveb', debug == "1")


@app.route("/vebcop", methods=['GET'])
def endpoint_vebcop_plain():
    log_endpoint_debug('/vebcop')
    return veb_cop('vebcop', False)


@app.route("/vebcop/{debug}", methods=['GET'])
def endpoint_vebcop(debug: int):
    log_endpoint_debug(f'/vebcop/{debug}')
    return veb_cop('vebcop', debug == "1")


@app.route("/btc", methods=['GET'])
def endpoint_btc_plain():
    log_endpoint_debug('/btc')
    return crypto('btc', 'usd', False)


@app.route("/btc/{debug}", methods=['GET'])
def endpoint_btc(debug: int):
    log_endpoint_debug(f'/btc/{debug}')
    return crypto('btc', 'usd', debug == "1")


@app.route("/eth", methods=['GET'])
def endpoint_eth_plain():
    log_endpoint_debug('/eth')
    return crypto('eth', 'usd', False)


@app.route("/eth/{debug}", methods=['GET'])
def endpoint_eth(debug: int):
    log_endpoint_debug(f'/eth/{debug}')
    return crypto('eth', 'usd', debug == "1")


@app.route("/crypto/{symbol}", methods=['GET'])
def endpoint_crypto_plain(symbol: str):
    log_endpoint_debug(f'/crypto/{symbol}')
    return crypto(symbol, 'usd', False)


@app.route("/crypto/{symbol}/{debug}", methods=['GET'])
def endpoint_crypto(symbol: str, debug: int):
    log_endpoint_debug(f'/crypto/{symbol}/{debug}')
    return crypto(symbol, 'usd', debug == "1")


@app.route("/crypto_wc/{symbol}/{currency}/{debug}")
def endpoint_crypto_curr(symbol: str, currency: str, debug: int):
    log_endpoint_debug(f'/crypto/{symbol}/{currency}/{debug}')
    return crypto(symbol, currency, debug == "1")
