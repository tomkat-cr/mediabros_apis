# index.py
# FastAPI implementation for Project: mediabros_apis
# 2023-01-24 | CR
#
import logging
from typing import Union

from fastapi import FastAPI, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from a2wsgi import ASGIMiddleware
from pydantic import BaseModel

from chalicelib.utility_password import get_password_hash
from chalicelib.utility_jwt import (
    Token, login_for_access_token, get_current_active_user)
from chalicelib.utility_date import get_formatted_date
from chalicelib.utility_general import (
    get_command_line_args, log_endpoint_debug, log_debug, log_normal)
from chalicelib.model_users import User
from chalicelib.api_openai import openai_api_with_defaults
from chalicelib.api_currency_exchange import (
    crypto, usdcop, usdveb, veb_cop, usdveb_full, usdveb_monitor)
from chalicelib.request_processing import request_processing


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


params = get_command_line_args()
if params['mode'] == 'cli':
    apiResponse = request_processing(params.get('body', ''))
    log_normal(apiResponse)

api = FastAPI()
app = ASGIMiddleware(api)
log_normal(f'Mediabros APIs started [FastAPI]. {get_formatted_date()}')


# JWT Authentication EndPoints


@api.post("/token", response_model=Token)
async def login_for_access_token_endpoint(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    log_endpoint_debug('/token')
    return login_for_access_token(form_data)


@api.get("/pget")
async def pget(p: str):
    log_endpoint_debug('/pget')
    return dict({'password_hashed': get_password_hash(p)})


# @api.get("/users/me/", response_model=User)
# async def read_users_me(
#   current_user: User = Depends(get_current_active_user)
# ):
#     log_endpoint_debug('/users/me/')
#     return current_user


# @app.get("/users/me/items/")
# async def read_own_items(
#   current_user: User = Depends(get_current_active_user)
# ):
#     return [{"item_id": "Foo", "owner": current_user.username}]


# This API specific EndPoints


class Body(BaseModel):
    q: Union[str, None] = None
    debug: Union[int, None] = None
    p: Union[str, None] = None
    m: Union[str, None] = None
    t: Union[str, None] = None
    mt: Union[str, None] = None


@api.get("/query_params/")
async def api_query_params(request: Request):
    log_endpoint_debug('/query_params')
    api_response = request.query_params
    log_debug(api_response)
    return api_response


@api.post("/ai")
async def ai_post(
    body: Body,
    current_user: User = Depends(get_current_active_user)
):
    log_endpoint_debug('/ai POST')
    form_params = dict(body)
    log_debug(f'ai_post: body = {str(form_params)}')
    api_response = openai_api_with_defaults(form_params)
    log_debug(f'ai_post: api_response = {api_response}')
    return api_response


@api.get("/ai")
async def ai_get(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    log_endpoint_debug('/ai GET')
    log_debug(f'ai_get: request = {request.query_params}')
    api_response = openai_api_with_defaults(request.query_params)
    log_debug(f'ai_get: api_response = {api_response}')
    return api_response


@api.get("/codex")
async def codex_get(
    request: Request,
    current_user: User = Depends(get_current_active_user)
):
    log_endpoint_debug('/codex')
    request_params = dict(request.query_params)
    request_params['m'] = 'code-davinci-002'
    log_debug(f'codex_get: request = {request_params}')
    api_response = openai_api_with_defaults(request_params)
    log_debug(f'codex_get: api_response = {api_response}')
    return api_response


@api.get("/usdcop")
def endpoint_usdcop_plain():
    log_endpoint_debug('/usdcop')
    return usdcop(False)


@api.get("/usdcop/{debug}")
def endpoint_usdcop(debug: int):
    log_endpoint_debug(f'/usdcop/{debug}')
    return usdcop(debug == 1)


@api.get("/usdveb")
def endpoint_usdveb_plain():
    log_endpoint_debug('/usdveb')
    return usdveb(False)


@api.get("/usdveb/{debug}")
def endpoint_usdveb(debug: int):
    log_endpoint_debug(f'/usdveb/{debug}')
    return usdveb(debug == 1)


@api.get("/usdveb_full")
def endpoint_usdveb_full_plain():
    log_endpoint_debug('/usdveb_full')
    return usdveb_full(False)


@api.get("/usdveb_full/{debug}")
def endpoint_usdveb_full(debug: int):
    log_endpoint_debug(f'/usdveb_full/{debug}')
    return usdveb_full(str(debug) == "1")


@api.get("/usdveb_monitor")
def endpoint_usdveb_monitor_plain():
    log_endpoint_debug('/usdveb_monitor')
    return usdveb_monitor(False)


@api.get("/usdveb_monitor/{debug}")
def endpoint_usdveb_monitor(debug: int):
    log_endpoint_debug(f'/usdveb_monitor/{debug}')
    return usdveb_monitor(str(debug) == "1")


@api.get("/copveb")
def endpoint_copveb_plain():
    log_endpoint_debug('/copveb')
    return veb_cop('copveb', False)


@api.get("/copveb/{debug}")
def endpoint_copveb(debug: int):
    log_endpoint_debug(f'/copveb/{debug}')
    return veb_cop('copveb', debug == 1)


@api.get("/vebcop")
def endpoint_vebcop_plain():
    log_endpoint_debug('/vebcop')
    return veb_cop('vebcop', False)


@api.get("/vebcop/{debug}")
def endpoint_vebcop(debug: int):
    log_endpoint_debug(f'/vebcop/{debug}')
    return veb_cop('vebcop', debug == 1)


@api.get("/btc")
def endpoint_btc_plain():
    log_endpoint_debug('/btc')
    return crypto('btc', 'usd', False)


@api.get("/btc/{debug}")
def endpoint_btc(debug: int):
    log_endpoint_debug(f'/btc/{debug}')
    return crypto('btc', 'usd', debug == 1)


@api.get("/eth")
def endpoint_eth_plain():
    log_endpoint_debug('/eth')
    return crypto('eth', 'usd', False)


@api.get("/eth/{debug}")
def endpoint_eth(debug: int):
    log_endpoint_debug(f'/eth/{debug}')
    return crypto('eth', 'usd', debug == 1)


@api.get("/crypto/{symbol}")
def endpoint_crypto_plain(symbol: str):
    log_endpoint_debug(f'/crypto/{symbol}')
    return crypto(symbol, 'usd', False)


@api.get("/crypto/{symbol}/{debug}")
def endpoint_crypto(symbol: str, debug: int):
    log_endpoint_debug(f'/crypto/{symbol}/{debug}')
    return crypto(symbol, 'usd', debug == 1)


@api.get("/crypto/{symbol}/{currency}/{debug}")
def endpoint_crypto_curr(symbol: str, currency: str, debug: int):
    log_endpoint_debug(f'/crypto/{symbol}/{currency}/{debug}')
    return crypto(symbol, currency, debug == 1)
