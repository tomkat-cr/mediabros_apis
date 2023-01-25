import logging

# from typing import Union, Any

from fastapi import FastAPI, Request
from a2wsgi import ASGIMiddleware

from .openai_api import openai_api_with_defaults
# from pydantic import BaseModel

# from .whatsapp_webhook import whatsapp_webhook_get, whatsapp_webhook_post
# from .whatsapp_send_message import send_whatsapp_message
# from .whatsapp_send_message import send_whatsapp_template

from .date_utilities import get_formatted_date
from .general_utilities import get_command_line_args
from .currency_exchange_apis import crypto, usdcop, usdveb, veb_cop


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


params = get_command_line_args()
# if params['mode'] == 'cli':
#   apiResponse = whatsapp_webhook_post(params.get('body'))
#   print(apiResponse)

api = FastAPI()
app = ASGIMiddleware(api)


# EndPoints


@api.get("/query_params/")
async def api_query_params(request: Request):
    print('---------')
    print(get_formatted_date())
    print('/query_params')
    api_response = request.query_params
    print(api_response)
    return api_response


# class Body(BaseModel):
#     object: Union[str, None] = None
#     entry: Union[Any, None] = None


# @api.post("/webhook")
# async def webhook_post(body: Body):
#     print('---------')
#     print(get_formatted_date())
#     print(f'webhook_post: body = {str(body)}')
#     api_response = whatsapp_webhook_post(body)
#     print(f'webhook_post: api_response = {api_response}')
#     return api_response


# @api.get("/send_template")
# def send_template(phone, template='hello_world'):
#     print('---------')
#     print(get_formatted_date())
#     print('send_template')
#     print(f'phone_number = {phone}')
#     print(f'template = {template}')
#     print('send_whatsapp_template - Begin...')
#     api_response = send_whatsapp_template(phone, template)
#     print('send_whatsapp_template - End...')
#     print(api_response)
#     return api_response


# @api.get("/send_message")
# def send_message(phone, message):
#     print('---------')
#     print(get_formatted_date())
#     print('send_message')
#     print(f'phone_number = {phone}')
#     print(f'message = {message}')
#     api_response = send_whatsapp_message(phone, message)
#     return api_response


@api.get("/ai")
async def ai_get(request: Request):
    print('---------')
    print(get_formatted_date())
    print(f'ai_get: request = {request.query_params}')
    api_response = openai_api_with_defaults(request.query_params)
    print(f'ai_get: api_response = {api_response}')
    return api_response


@api.get("/usdcop")
def endpoint_usdcop_plain():
    return usdcop(False)


@api.get("/usdcop/{debug}")
def endpoint_usdcop(debug: int):
    return usdcop(debug == 1)


@api.get("/usdvef")
def endpoint_usdvef_plain():
    return usdveb(False)


@api.get("/usdvef/{debug}")
def endpoint_usdvef(debug: int):
    return usdveb(debug == 1)


@api.get("/copveb")
def endpoint_copveb_plain():
    return veb_cop('copveb', False)


@api.get("/copveb/{debug}")
def endpoint_copveb(debug: int):
    return veb_cop('copveb', debug == 1)


@api.get("/vebcop")
def endpoint_vebcop_plain():
    return veb_cop('vebcop', False)


@api.get("/vebcop/{debug}")
def endpoint_vebcop(debug: int):
    return veb_cop('vebcop', debug == 1)


@api.get("/btc")
def endpoint_btc_plain():
    return crypto('btc', 'usd', False)


@api.get("/btc/{debug}")
def endpoint_btc(debug: int):
    return crypto('btc', 'usd', debug == 1)


@api.get("/eth")
def endpoint_eth_plain():
    return crypto('eth', 'usd', False)


@api.get("/eth/{debug}")
def endpoint_eth(debug: int):
    return crypto('eth', 'usd', debug == 1)


@api.get("/crypto/{symbol}")
def endpoint_crypto_plain(symbol: str):
    return crypto(symbol, 'usd', False)


@api.get("/crypto/{symbol}/{debug}")
def endpoint_crypto(symbol: str, debug: int):
    return crypto(symbol, 'usd', debug == 1)
