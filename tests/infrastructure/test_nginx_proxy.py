"""Tests the NGINX proxy infrastructure."""

import requests


def test_connectable():
    """Ensure the machine can connect to NGINX."""
    response = requests.get('http://localhost/', timeout=3)
    assert response.status_code == 200
