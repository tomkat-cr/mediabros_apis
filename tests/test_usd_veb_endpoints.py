"""
USD/VEB endpoints test
"""

import pytest

# http://127.0.0.1:5001/usdveb
#
# Returns:
# BCV official exchange rate: 95.08 Bs/USD.
# Effective Date: Lunes, 26 Mayo  2025


@pytest.mark.parametrize("debug", ["", "/0", "/2"])
def test_usdveb_plain(client, debug):
    """Test the /usdveb endpoint."""
    response = client.get(f'/usdveb{debug}')
    assert response.status_code == 200
    assert response.text is not None
    assert 'BCV official exchange rate:' in response.text
    assert 'Effective Date:' in response.text


# http://127.0.0.1:5001/usdveb/1
#
# Returns:
# BCV official exchange rates: {'error': False, 'error_message': [], 'data':
# {'euro': {'symbol': 'EUR', 'value': 107.79577996}, 'yuan': {'symbol': 'CNY',
# 'value': 13.24271249}, 'lira': {'symbol': 'TRY', 'value': 2.43636456},
# 'rublo': {'symbol': 'RUB', 'value': 1.19590782}, 'dolar': {'symbol': 'USD',
# 'value': 95.084}, 'effective_date': 'Lunes, 26 Mayo  2025',
# 'run_timestamp': '2025-05-24 11:50:00 UTC'}}


def test_usdveb_debug(client):
    """Test the /usdveb/{debug} endpoint."""
    response = client.get('/usdveb/1')
    assert response.status_code == 200
    assert response.text is not None
    assert 'BCV official exchange rates:' in response.text
    assert 'euro' in response.text
    assert 'yuan' in response.text
    assert 'lira' in response.text
    assert 'rublo' in response.text
    assert 'dolar' in response.text
    assert "'symbol': 'EUR'" in response.text
    assert "'symbol': 'CNY'" in response.text
    assert "'symbol': 'TRY'" in response.text
    assert "'symbol': 'RUB'" in response.text
    assert "'symbol': 'USD'" in response.text
    assert 'effective_date' in response.text
    assert 'run_timestamp' in response.text
