import os
import datetime
import requests
from chalicelib.utility_general import get_api_standard_response, log_warning
from chalicelib.utility_telegram import report_error_to_tg_group
from chalicelib.utility_general import log_debug


DEBUG = os.getenv("CODE_DEBUG", "0") == "1"
log_debug(f"[DEBUG] {DEBUG}")


# Exchange APIs


def crypto_api(symbol, currency):
    api_response = get_api_standard_response()
    currency = currency.upper()
    symbol = symbol.upper()
    # url = 'https://min-api.cryptocompare.com/data/price?' + \
    # 'fsym=ETH&tsyms=BTC,USD,EUR'
    url = 'https://min-api.cryptocompare.com/data/price?' + \
        f'fsym={symbol}&tsyms={currency}'
    try:
        response = requests.get(url)
        # Ok response:
        # {'USD': 0.2741}
        # Error response:
        # {'Response': 'Error', 'Message': 'fsym is a required param.',
        # 'HasWarning': False, 'Type': 2, 'RateLimit': {}, 'Data': {},
        # 'ParamWithError': 'fsym'}
    except Exception as err:
        api_response['error'] = True
        api_response['error_message'] = str(err)
    else:
        if response.status_code != 200:
            api_response['error'] = True
            api_response['error_message'] = 'ERROR reading the ' + \
                'min-api.cryptocompare.com API'
        else:
            api_response['data'] = response.json()
            if api_response['data'].get('Response', '') == 'Error':
                api_response['error'] = True
                api_response['error_message'] = "ERROR: " + \
                    api_response['data']['Message']
    report_error_to_tg_group(api_response)
    return api_response


def veb_monitor_api():
    # url = 'https://monitor-exchange-rates.vercel.app/get_exchange_rates'
    url = os.getenv("MONITOR_EXCHANGE_URL")
    if not url:
        api_response = veb_monitor_api_from_class()
    else:
        api_response = get_api_resp_from_url(url, "Monitor USD/Bs")
    _ = DEBUG and log_debug(f'veb_monitor_api | api_response:\n{api_response}')
    return api_response


def veb_monitor_api_from_class():
    from monitor_exchange_rates.monitor import get_monitor_exchange_rates
    api_response = get_monitor_exchange_rates()
    return get_api_resp_from_class_wrapper(api_response)


def veb_bcv_api():
    # url = 'https://bcv-exchange-rates.vercel.app/get_exchange_rates'
    url = os.getenv("VEB_EXCHANGE_URL")
    if not url:
        api_response = veb_bcv_api_from_class()
    else:
        api_response = get_api_resp_from_url(url, "BCV official USD/Bs")
    _ = DEBUG and log_debug(f'veb_bcv_api | api_response:\n{api_response}')
    return api_response


def veb_bcv_api_from_class():
    from bcv_exchange_rates.bcv import get_bcv_exchange_rates
    api_response = get_bcv_exchange_rates()
    return get_api_resp_from_class_wrapper(api_response)


def get_api_resp_from_class_wrapper(api_resp):
    api_response = get_api_standard_response()
    api_response['data'] = api_resp
    api_response['error'] = api_resp['error']
    api_response['error_message'] = api_resp['error_message']
    return api_response


def get_api_resp_from_url(url, name):
    api_response = get_api_standard_response()
    try:
        response = requests.get(url)
    except Exception as err:
        api_response['error'] = True
        api_response['error_message'] = str(err)
    else:
        if response.status_code == 200:
            result = response.json()
            api_response['data'] = dict(result)
            api_response['error'] = result['error']
            api_response['error_message'] = result['error_message']
        else:
            api_response['error'] = True
            api_response['error_message'] = f'ERROR reading {name} API'
    report_error_to_tg_group(api_response)
    return api_response


def veb_dolartoday_api():
    # DEPRECATED
    api_response = get_api_standard_response()
    url = 'https://s3.amazonaws.com/dolartoday/data.json'
    try:
        response = requests.get(url)
    except Exception as err:
        api_response['error'] = True
        api_response['error_message'] = str(err)
    else:
        if response.status_code == 200:
            api_response['data'] = response.json()
        else:
            api_response['error'] = True
            api_response['error_message'] = 'ERROR reading DolarToday API'
    report_error_to_tg_group(api_response)
    _ = DEBUG and log_debug("veb_dolartoday_api | " +
                            f"api_response:\n{api_response}")
    return api_response


def cop_api():
    # url = 'https://cop-exchange-rates.vercel.app/get_exchange_rates'
    url = os.getenv("COP_EXCHANGE_URL")
    if not url:
        api_response = cop_api_from_class()
    else:
        api_response = get_api_resp_from_url(url, "Colombian Peso USD/COP")
    _ = DEBUG and log_debug(f"cop_api | api_response:\n{api_response}")
    return api_response


def cop_api_from_class():
    from cop_exchange_rates.cop import get_cop_exchange_rates
    api_response = get_cop_exchange_rates()
    return get_api_resp_from_class_wrapper(api_response)


# Middleware


def crypto(symbol, currency, debug):
    currency = currency.upper()
    symbol = symbol.upper()
    api_response = crypto_api(symbol, currency)
    if api_response['error']:
        response_message = api_response['error_message']
        if debug:
            response_message += f"\n{api_response['data']}"
        return response_message
    result = api_response['data']
    if debug:
        response_message = f'The {symbol} exchange rate is: {result}'
    else:
        exchange_rate = f'{float(result[currency]):.2f}' \
            if currency in result \
            else f"ERROR: no {currency} element in API result"
        response_message = f'The {symbol} to {currency} ' + \
            f'exchange rate is: {exchange_rate}'
    _ = DEBUG and log_debug(f"crypto | response_message:\n{response_message}")
    return response_message


def eth(debug):
    return crypto('eth', 'usd', debug)


def btc(debug):
    return crypto('btc', 'usd', debug)


def veb_bcv(debug):
    api_response = veb_bcv_api()
    if api_response['error']:
        return api_response['error_message']
    result = api_response['data']
    if debug:
        response_message = f'BCV official exchange rates: {result}'
    else:
        exchange_rate = float(result['data']['dolar']['value'])
        effective_date = result['data']['effective_date']
        response_message = 'BCV official exchange rate:' + \
            f' {exchange_rate:.2f} Bs/USD.\n' + \
            f'Effective Date: {effective_date}'
    _ = DEBUG and log_debug(f"veb_bcv | response_message:\n{response_message}")
    return response_message


def veb_monitor(debug):
    api_response = veb_monitor_api()
    response_message = 'Monitor exchange rate:\n'
    if api_response['error']:
        response_message += "\n".join(api_response['error_message'])
        return response_message
    result = api_response['data']
    if debug:
        response_message = f'Monitor exchange rates: {result}'
    else:
        exchange_rate = [
            f"  {symbol_data['symbol']}: {symbol_data['value']}"
            for _, symbol_data in result['data'].items()
            if isinstance(symbol_data, dict) and "value" in symbol_data
        ]
        exchange_rate = "\n".join(exchange_rate)
        from_date = result['data']['effective_date']
        response_message += f'{exchange_rate}\n' + \
            f'Effective Date: {from_date}'
    _ = DEBUG and log_debug("veb_monitor | " +
                            f"response_message:\n{response_message}")
    return response_message


def veb_dolartoday(debug):
    api_response = veb_dolartoday_api()
    if api_response['error']:
        return api_response['error_message']
    result = api_response['data']
    if debug:
        response_message = f'DolarToday exchange rate: {result}'
    else:
        exchange_rate = float(result['USD']['transferencia'])
        from_date = result['_timestamp']['fecha_corta']
        response_message = 'DolarToday exchange rate:' + \
            f' {exchange_rate:.2f} Bs/USD.\n' + \
            f'Date: {from_date}'
    _ = DEBUG and log_debug("veb_dolartoday | " +
                            f"response_message:\n{response_message}")
    return response_message


def usdveb(debug):
    response_message = veb_bcv(debug)
    response_message += '\n\n' + veb_monitor(debug)
    # response_message += '\n\n' + veb_dolartoday(debug)
    _ = DEBUG and log_debug("usdveb | " +
                            f"response_message:\n{response_message}")
    return response_message


def usdcop(debug):
    try:
        api_response = cop_api()
        if api_response['error']:
            return api_response['error_message']
        result = api_response['data']['data']['official_cop']['data']
        if debug:
            response_message = 'The COP/USD exchange rate is:' + \
                f" {api_response['data']['data']}"
        else:
            official_exchange_rate = float(result['valor'])
            official_exchange_rate_bank = float(result['bank_value'])
            official_exchange_rate_bank_prec = float(
                result['bank_value_percent']
            )
            from_date = datetime.date.strftime(
                datetime.datetime.strptime(
                    result['vigenciadesde'],
                    "%Y-%m-%dT%H:%M:%S.000"
                ), "%B %d, %Y"
            )
            to_date = datetime.date.strftime(
                datetime.datetime.strptime(
                    result['vigenciahasta'],
                    "%Y-%m-%dT%H:%M:%S.000"
                ), "%B %d, %Y"
            )

            result = api_response['data']['data']['google_cop']['data']
            google_exchange_rate = float(result['value'])
            google_exchange_rate_bank = float(result['bank_value'])
            google_exchange_rate_bank_prec = float(
                result['bank_value_percent']
            )
            google_effective_date = result['effective_date']

            response_message = 'COP official exchange rate: ' + \
                f'{official_exchange_rate:.2f} COP/USD.\n' + \
                'COP official exchange for bank transfers: ' + \
                f'{official_exchange_rate_bank:.2f} COP/USD' + \
                f' (+{official_exchange_rate_bank_prec:.2f}%).\n' + \
                f'From: {from_date}, to: {to_date}\n' + \
                '\n' + \
                'COP google exchange rate: ' + \
                f'{google_exchange_rate:.2f} COP/USD.\n' + \
                'COP google exchange for bank transfers: ' + \
                f'{google_exchange_rate_bank:.2f} COP/USD' + \
                f' (+{google_exchange_rate_bank_prec:.2f}%).\n' + \
                f'Effective date: {google_effective_date}.'

    except Exception as err:
        response_message = f'ERROR in usdcop: {err}'
        log_warning(response_message)
    _ = DEBUG and log_debug(f"usdcop | response_message:\n{response_message}")
    return response_message


def veb_cop(currency_pair, debug):
    veb_response = veb_bcv_api()
    cop_response = cop_api()
    if veb_response['error']:
        return veb_response['error_message']
    if cop_response['error']:
        return cop_response['error_message']
    result = veb_response['data']
    if debug:
        response_message = f'BCV official: {veb_response["data"]}' + \
            '\n' + \
            f'COP official: {cop_response["data"]}'
    else:
        veb_exchange_rate = float(result['data']['dolar']['value'])
        effective_date = result['data']['effective_date']
        result = cop_response['data']['data']['official_cop']['data']
        cop_exchange_rate = float(result['valor'])
        if currency_pair == 'copveb':
            exchange_rate = cop_exchange_rate / veb_exchange_rate
            suffix = 'COP/Bs'
        else:
            exchange_rate = veb_exchange_rate / cop_exchange_rate
            suffix = 'Bs/COP'
        response_message = 'Exchange rate:' + \
            f' {exchange_rate:.4f} {suffix}.\n' + \
            f'Effective Date: {effective_date}'
    _ = DEBUG and log_debug(f"veb_cop | response_message:\n{response_message}")
    return response_message
