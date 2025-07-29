"""
VEB/COP endpoints test
"""

import pytest

# http://127.0.0.1:5001/vebcop
#
# Returns:
# Exchange rate: 0.0228 Bs/COP.
# Effective Date: Lunes, 26 Mayo  2025


@pytest.mark.parametrize("debug", ["", "/0", "/2"])
def test_vebcop_plain(client, debug):
    response = client.get(f'/vebcop{debug}')
    assert response.status_code == 200
    assert response.text is not None
    assert 'Exchange rate:' in response.text
    assert 'Bs/COP.' in response.text
    assert 'Effective Date:' in response.text


# http://127.0.0.1:5001/vebcop/1
#
# Returns:
# BCV official: {'error': False, 'error_message': [], 'data': {'euro':
# {'symbol': 'EUR', 'value': 107.79577996}, 'yuan': {'symbol': 'CNY',
# 'value': 13.24271249}, 'lira': {'symbol': 'TRY', 'value': 2.43636456},
# 'rublo': {'symbol': 'RUB', 'value': 1.19590782}, 'dolar': {'symbol': 'USD',
# 'value': 95.084}, 'effective_date': 'Lunes, 26 Mayo  2025',
# 'run_timestamp': '2025-05-25 11:09:53 UTC'}}
# COP official: {'error': False, 'error_message': '', 'data': {'google_cop':
# {'error': False, 'error_message': '', 'data': {'unit': 'USD / COP',
# 'value': '4170.1190', 'bank_value': '4170.12', 'bank_value_percent': 0.0,
# 'effective_date': 'May 23, 11:34:04\u202fPM UTC'}, 'run_timestamp':
# '2025-05-25 11:09:53 UTC'}, 'official_cop': {'error': False,
# 'error_message': '', 'data': {'valor': '4165.41', 'unidad': 'COP',
# 'vigenciadesde': '2025-05-24T00:00:00.000', 'vigenciahasta':
# '2025-05-27T00:00:00.000', ':id': 'row-6z9a-eepe~rxcy',
# 'bank_value': '4165.41', 'bank_value_percent': 0.0}, 'run_timestamp':
# '2025-05-25 11:09:53 UTC'}}}


def test_vebcop_debug(client):
    response = client.get('/vebcop/1')
    assert response.status_code == 200
    assert response.text is not None
    assert 'COP official:' in response.text
    assert 'google_cop' in response.text
    assert 'official_cop' in response.text
    assert 'run_timestamp' in response.text
    assert 'effective_date' in response.text
    assert 'BCV official:' in response.text
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
