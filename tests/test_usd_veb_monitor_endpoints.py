"""
USD/VEB MonitorDolarVenezuela endpoint test
"""

import pytest

# http://127.0.0.1:5001/usdveb_monitor
#
# Returns:
# Monitor exchange rate:
#   Dólar BCV (Oficial): 95.08
#   Dólar Paralelo: 109.2
#   Dólar Promedio: 102.14
#   El Dorado P2P: 134.6
#   Binance P2P: 133.0
#   @EnParaleloVzlaVIP: 110.4
# Effective Date: 2025-05-24


# @pytest.mark.parametrize("debug", ["", "/0", "/2"])
# def test_usdveb_monitor(client, debug):
def test_usdveb_monitor(client):
    """Test the /usdveb_monitor endpoint."""
    debug = ""
    response = client.get(f'/usdveb_monitor{debug}')
    assert response.status_code == 200
    assert response.text is not None
    assert 'Monitor exchange rate:' in response.text
    assert 'Dólar BCV (Oficial):' in response.text
    assert 'Dólar Paralelo:' in response.text
    assert 'Dólar Promedio:' in response.text
    assert 'El Dorado P2P:' in response.text
    assert 'Binance P2P:' in response.text
    assert '@EnParaleloVzlaVIP:' in response.text
    assert 'Effective Date:' in response.text


# http://127.0.0.1:5001/usdveb_monitor
#
# Returns:
# Monitor exchange rates: {'error': False, 'error_message': [], 'data':
# {'usd_bcv': {'symbol': 'Dólar BCV (Oficial)', 'value': 95.08,
# 'effective_time': '7:30 AM', 'effective_date': '24/05/2025'},
# 'usd_paralelo': {'symbol': 'Dólar Paralelo', 'value': 109.2,
# 'effective_time': '01:00 PM', 'effective_date': '02/05/2025'},
# 'usd_promedio': {'symbol': 'Dólar Promedio', 'value': 102.14,
# 'effective_time': '7:30 AM', 'effective_date': '24/05/2025'},
# 'eldorado_p2p': {'symbol': 'El Dorado P2P', 'value': 134.64,
# 'effective_time': '7:30 AM', 'effective_date': '24/05/2025'},
# 'binance_p2p': {'symbol': 'Binance P2P', 'value': 133.0,
# 'effective_time': '7:30 AM', 'effective_date': '24/05/2025'},
# 'enparalelovzla_p2p': {'symbol': '@EnParaleloVzlaVIP', 'value': 110.4,
# 'effective_time': '7:30 AM', 'effective_date': '24/05/2025'},
# 'effective_date': '2025-05-24', 'run_timestamp': '2025-05-24 11:50:15 UTC'}}

def test_usdveb_monitor_debug(client):
    """Test the /usdveb_monitor/{debug} endpoint."""
    response = client.get('/usdveb_monitor/1')
    assert response.status_code == 200
    assert response.text is not None
    assert 'Monitor exchange rates:' in response.text
    assert "'usd_bcv':" in response.text
    assert "'usd_paralelo':" in response.text
    assert "'usd_promedio':" in response.text
    assert "'eldorado_p2p':" in response.text
    assert "'binance_p2p':" in response.text
    assert "'enparalelovzla_p2p':" in response.text
    assert "'effective_date':" in response.text
    assert "'run_timestamp':" in response.text


# USD/VEB Full


# http://127.0.0.1:5001/usdveb_full
#
# Returns:
# BCV official exchange rate: 95.08 Bs/USD.
# Effective Date: Lunes, 26 Mayo  2025
#
# Monitor exchange rate:
#   Dólar BCV (Oficial): 95.08
#   Dólar Paralelo: 109.2
#   Dólar Promedio: 102.14
#   El Dorado P2P: 134.6
#   Binance P2P: 133.0
#   @EnParaleloVzlaVIP: 110.4
# Effective Date: 2025-05-24


@pytest.mark.parametrize("debug", ["", "/0", "/2"])
def test_usdveb_full(client, debug):
    response = client.get(f'/usdveb_full{debug}')
    assert response.status_code == 200
    assert response.text is not None
    assert 'BCV official exchange rate:' in response.text
    assert 'Monitor exchange rate:' in response.text
    assert 'Dólar BCV (Oficial):' in response.text
    assert 'Dólar Paralelo:' in response.text
    assert 'Dólar Promedio:' in response.text
    assert 'El Dorado P2P:' in response.text
    assert 'Binance P2P:' in response.text
    assert '@EnParaleloVzlaVIP:' in response.text
    assert 'Effective Date:' in response.text


# http://127.0.0.1:5001/usdveb_full/1
#
# Returns:
# BCV official exchange rates: {'error': False, 'error_message': [], 'data':
# {'euro': {'symbol': 'EUR', 'value': 107.79577996}, 'yuan': {'symbol': 'CNY',
# 'value': 13.24271249}, 'lira': {'symbol': 'TRY', 'value': 2.43636456},
# 'rublo': {'symbol': 'RUB', 'value': 1.19590782}, 'dolar': {'symbol': 'USD',
# 'value': 95.084}, 'effective_date': 'Lunes, 26 Mayo  2025',
# 'run_timestamp': '2025-05-24 11:50:00 UTC'}}
#
# Monitor exchange rates: {'error': False, 'error_message': [], 'data':
# {'usd_bcv': {'symbol': 'Dólar BCV (Oficial)', 'value': 95.08,
# 'effective_time': '7:30 AM', 'effective_date': '24/05/2025'},
# 'usd_paralelo': {'symbol': 'Dólar Paralelo', 'value': 109.2,
# 'effective_time': '01:00 PM', 'effective_date': '02/05/2025'},
# 'usd_promedio': {'symbol': 'Dólar Promedio', 'value': 102.14,
# 'effective_time': '7:30 AM', 'effective_date': '24/05/2025'},
# 'eldorado_p2p': {'symbol': 'El Dorado P2P', 'value': 134.64,
# 'effective_time': '7:30 AM', 'effective_date': '24/05/2025'},
# 'binance_p2p': {'symbol': 'Binance P2P', 'value': 133.0,
# 'effective_time': '7:30 AM', 'effective_date': '24/05/2025'},
# 'enparalelovzla_p2p': {'symbol': '@EnParaleloVzlaVIP', 'value': 110.4,
# 'effective_time': '7:30 AM', 'effective_date': '24/05/2025'},
# 'effective_date': '2025-05-24', 'run_timestamp': '2025-05-24 11:50:15 UTC'}}


def test_usdveb_full_debug(client):
    response = client.get('/usdveb_full/1')
    assert response.status_code == 200
    assert response.text is not None
    assert 'BCV official exchange rates:' in response.text
    assert 'Monitor exchange rates:' in response.text
    assert "'usd_bcv':" in response.text
    assert "'usd_paralelo':" in response.text
    assert "'usd_promedio':" in response.text
    assert "'eldorado_p2p':" in response.text
    assert "'binance_p2p':" in response.text
    assert "'enparalelovzla_p2p':" in response.text
    assert "'effective_date':" in response.text
    assert "'run_timestamp':" in response.text
