"""
USD/COP endpoints test
"""

import pytest


# http://127.0.0.1:5001/usdcop
#
# Returns:
# COP official exchange rate: 4165.41 COP/USD.
# COP official exchange for bank transfers: 4165.41 COP/USD (+0.00%).
# From: May 24, 2025, to: May 27, 2025
#
# COP google exchange rate: 4170.12 COP/USD.
# COP google exchange for bank transfers: 4170.12 COP/USD (+0.00%).
# Effective date: May 23, 11:34:04 PM UTC.


@pytest.mark.parametrize("debug", ["", "/0", "/2"])
def test_usdcop_plain(client, debug):
    """Test the /usdcop endpoint."""
    response = client.get(f'/usdcop{debug}')
    assert response.status_code == 200
    assert response.text is not None
    assert 'COP official exchange rate:' in response.text
    assert 'COP google exchange rate:' in response.text
    assert 'From:' in response.text
    assert ', to:' in response.text
    assert 'Effective date:' in response.text


# http://127.0.0.1:5001/usdcop/1
#
# Returns:
# The COP/USD exchange rate is: {'google_cop': {'error': False,
# 'error_message': '', 'data': {'unit': 'USD / COP', 'value': '4170.1190',
# 'bank_value': '4170.12', 'bank_value_percent': 0.0,
# 'effective_date': 'May 23, 11:34:04\u202fPM UTC'},
# 'run_timestamp': '2025-05-24 11:42:09 UTC'}, 'official_cop':
#  {'error': False, 'error_message': '', 'data': {'valor': '4165.41',
# 'unidad': 'COP', 'vigenciadesde': '2025-05-24T00:00:00.000',
# 'vigenciahasta': '2025-05-27T00:00:00.000', ':id': 'row-6z9a-eepe~rxcy',
# 'bank_value': '4165.41', 'bank_value_percent': 0.0},
# 'run_timestamp': '2025-05-24 11:42:09 UTC'}}


def test_usdcop_debug(client):
    """Test the /usdcop/{debug} endpoint."""
    # Assuming '1' means debug enabled
    response = client.get('/usdcop/1')
    assert response.status_code == 200
    assert response.text is not None
    assert 'google_cop' in response.text
    assert 'official_cop' in response.text
    assert 'run_timestamp' in response.text
    assert 'bank_value' in response.text
    assert 'bank_value_percent' in response.text
    assert 'effective_date' in response.text
    assert 'vigenciadesde' in response.text
    assert 'vigenciahasta' in response.text
    assert 'valor' in response.text
    assert 'unidad' in response.text
    assert 'id' in response.text
