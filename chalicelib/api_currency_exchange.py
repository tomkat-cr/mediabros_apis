import datetime
import requests
from chalicelib.utility_general import get_api_standard_response, log_warning
from chalicelib.utility_telegram import report_error_to_tg_group


# ------------------------


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


def veb_bcv_api():
    api_response = get_api_standard_response()
    url = 'https://bcv-exchange-rates.vercel.app/get_exchange_rates'
    try:
        response = requests.get(url)
    except Exception as err:
        api_response['error'] = True
        api_response['error_message'] = str(err)
    else:
        if response.status_code == 200:
            result = response.json()
            api_response['data'] = result
            if result['error']:
                api_response['error'] = True
                api_response['error_message'] = result['error_message']
        else:
            api_response['error'] = True
            api_response['error_message'] = 'ERROR reading BCV official' + \
                ' USD/Bs API'
    report_error_to_tg_group(api_response)
    return api_response


def veb_dolartoday_api():
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
    return api_response


def cop_api():
    api_response = get_api_standard_response()
    url = 'https://cop-exchange-rates.vercel.app/get_exchange_rates'
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
            api_response['error_message'] = 'ERROR reading ' + \
                'Mediabros\' cop-exchange-rates API'
    report_error_to_tg_group(api_response)
    return api_response


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
    return response_message


def usdveb(debug):
    response_message = veb_bcv(debug)
    response_message += '\n\n' + veb_dolartoday(debug)
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
    return response_message
