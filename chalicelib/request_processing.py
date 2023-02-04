from chalicelib.api_openai import openai_api_with_defaults
from chalicelib.api_currency_exchange import usdcop, usdveb, veb_cop, crypto
from chalicelib.utility_general import log_normal


def request_processing(message):
    param_separated = message.split(" ")
    command = param_separated[0]
    param_separated.remove(command)
    debug = False
    if len(param_separated) >= 1:
        if param_separated[0] == '/debug':
            debug = True
            param_separated.remove('/debug')
    other_param = ' '.join(param_separated)

    log_normal('request_processing')
    log_normal(f'command: {command}')
    log_normal(f'debug: {debug}')
    log_normal(f'other_param: {other_param}')

    if command == '/ai':
        request = dict()
        request['q'] = other_param
        return openai_api_with_defaults(request)
    if command == '/codex':
        request = dict()
        request['q'] = other_param
        request['m'] = 'code-davinci-002'
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
