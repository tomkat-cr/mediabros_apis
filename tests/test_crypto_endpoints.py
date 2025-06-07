"""
CRYPTO endpoints test
"""

import pytest


# http://127.0.0.1:5001/crypto/btc
# http://127.0.0.1:5001/crypto/btc/0
# http://127.0.0.1:5001/crypto/btc/2
# http://127.0.0.1:5001/crypto/btc/
# http://127.0.0.1:5001/crypto/btc/usd
#
# Returns:
# The BTC to USD exchange rate is: 109437.64


@pytest.mark.parametrize("debug", ["", "/0", "/2", "/", "/usd"])
@pytest.mark.parametrize("symbol", ["btc", "eth", "ltc"], )
def test_crypto_btcusd_plain(client, symbol, debug):
    response = client.get(f'/crypto/{symbol}{debug}')
    assert response.status_code == 200
    assert response.text is not None
    assert f'The {symbol.upper()} to USD exchange rate is:' in response.text


# http://127.0.0.1:5001/crypto/btc/1
#
# Returns:
# The BTC exchange rate is: {'USD': 109456.35}


@pytest.mark.parametrize("symbol", ["btc", "eth", "ltc"])
def test_crypto_btcusd_debug(client, symbol):
    response = client.get(f'/crypto/{symbol}/1')
    assert response.status_code == 200
    assert response.text is not None
    assert f'The {symbol.upper()} exchange rate is:' in response.text
    assert "{'USD': " in response.text


# http://127.0.0.1:5001/crypto/btc1
#
# Returns:
# ERROR: cccagg_or_exchange market does not exist for this coin pair (BTC1-USD)

@pytest.mark.parametrize("debug", ["", "/0", "/2", "/"])
@pytest.mark.parametrize("symbol", ["btc1", "eth1"])
def test_crypto_btcusd_invalid(client, symbol, debug):
    response = client.get(f'/crypto/{symbol}{debug}')
    assert response.status_code == 200
    assert response.text is not None
    assert 'ERROR: cccagg_or_exchange market does not exist for' + \
           f' this coin pair ({symbol.upper()}-USD)' in response.text
