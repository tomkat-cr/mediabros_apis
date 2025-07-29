"""
INVALID endpoints test
"""

import pytest


# http://127.0.0.1:5001/invalid
# http://127.0.0.1:5001invalid
# http://127.0.0.1:5001/crypto_wc/btc/veb
#
# Returns:
# chalice.local.ForbiddenError: ({'x-amzn-RequestId':
#  'cfa5bf70-2945-4056-b1c2-c6c5d30ca788', 'x-amzn-ErrorType':
#  'UnauthorizedException'}, b'{"message": "Missing Authentication Token"}')


@pytest.mark.parametrize("endpoint", [
    "/invalid",
    "invalid",
    "/invalid/0",
    "/crypto/btc/usd/0",
    "/crypto/btc/usd/1",
    "/crypto_wc/btc",
    "/crypto_wc/btc/",
    "/crypto_wc/btc/veb",
    "/crypto_wc/btc/veb/",
])
def test_invalid_endpoint(client, endpoint):
    # Handle eventual ValueError
    try:
        response = client.get(endpoint)
    except Exception as err:
        # It has a space after the colon on purpose
        assert '{"message": "Missing Authentication Token"}' in str(err)
    else:
        assert response.status_code == 403
        assert response.text is not None
        # It doesn't have a space after the colon on purpose
        assert '{"message":"Missing Authentication Token"}' in response.text
