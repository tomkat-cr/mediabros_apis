"""
CRYPTO WC endpoints test
"""

import pytest


# http://127.0.0.1:5001/crypto_wc/btc/usd/0
#
# Returns:
# The BTC to USD exchange rate is: 109437.64


@pytest.mark.parametrize("symbol", ["btc", "eth", "ltc"])
def test_crypto_wc_btcusd_plain(client, symbol):
    response = client.get(f'/crypto_wc/{symbol}/usd/0')
    assert response.status_code == 200
    assert response.text is not None
    assert f'The {symbol.upper()} to USD exchange rate is:' in response.text


# http://127.0.0.1:5001/crypto_wc/btc/usd/1
#
# Returns:
# The BTC exchange rate is: {'USD': 109456.35}


@pytest.mark.parametrize("symbol", ["btc", "eth", "ltc"])
def test_crypto_wc_btcusd_debug(client, symbol):
    response = client.get(f'/crypto_wc/{symbol}/usd/1')
    assert response.status_code == 200
    assert response.text is not None
    assert f'The {symbol.upper()} exchange rate is:' in response.text
    assert "{'USD': " in response.text


# http://127.0.0.1:5001/crypto_wc/btc/veb/0
#
# Returns:
# ERROR: cccagg_or_exchange market does not exist for this coin pair (BTC-VEB)


@pytest.mark.parametrize("symbol", ["btc", "eth"])
@pytest.mark.parametrize("currency", ["veb", "eur1"])
def test_crypto_wc_btcveb_invalid(client, symbol, currency):
    response = client.get(f'/crypto_wc/{symbol}/{currency}/0')
    assert response.status_code == 200
    assert response.text is not None
    assert 'ERROR: cccagg_or_exchange market does not exist for' + \
           f' this coin pair ({symbol.upper()}-{currency.upper()})' \
           in response.text


# http://127.0.0.1:5001/crypto_wc/btc/veb/1
#
# Returns:
# ERROR: cccagg_or_exchange market does not exist for this coin pair (BTC-VEB)
# {'Response': 'Error', 'Message': 'cccagg_or_exchange market does not exist
#  for this coin pair (BTC-VEB)', 'HasWarning': False, 'Type': 2, 'RateLimit':
#  {}, 'Data': {}, 'Cooldown': 0}


@pytest.mark.parametrize("symbol", ["btc", "eth"])
@pytest.mark.parametrize("currency", ["veb", "eur1"])
def test_crypto_wc_btcveb_debug_invalid(client, symbol, currency):
    response = client.get(f'/crypto_wc/{symbol}/{currency}/1')
    assert response.status_code == 200
    assert response.text is not None
    assert 'ERROR: cccagg_or_exchange market does not exist for' + \
           f' this coin pair ({symbol.upper()}-{currency.upper()})' \
           in response.text
    assert "{'Response': 'Error', 'Message': 'cccagg_or_exchange market does" \
           + " not exist for this coin pair" \
           + f" ({symbol.upper()}-{currency.upper()})'" \
           + ", 'HasWarning': False, 'Type': 2, 'RateLimit': {" \
           + "}, 'Data': {" + "}, 'Cooldown': 0}" in response.text
