from .openai_api import openai_api_with_defaults
from .currency_exchange_apis import usdcop, usdveb, veb_cop, crypto


def request_processing(message):
    param_separated = message.split(" ")
    command = param_separated[0]
    other_param = ''
    debug = False
    if len(param_separated) > 1:
        if param_separated[1] == 'debug':
            debug = True
        else:
            other_param = param_separated[1]
    if command == '/ai':
        request = dict()
        request['question'] = other_param
        return openai_api_with_defaults(request)
    if command == '/cop':
        return usdcop(debug)
    if command == '/bs':
        return usdveb(debug)
    if command == '/copveb':
        return veb_cop('copveb', debug)
    if command == '/vebcop':
        return veb_cop('vebcop', debug)
    if command == '/btc':
        return crypto('btc', 'usd', debug)
    if command == '/eth':
        return crypto('eth', 'usd', debug)
    return f'ERROR: Invalid option: {message}'
