"""Orders' client for the catalog HTTP API (components/catalog/service.py).

Orders running as its own service reads prices over the network instead of importing the catalog.
CATALOG_URL points at the catalog service; today the call is plain HTTP.
"""
import json
import os
import urllib.request

CATALOG_URL = os.environ.get("CATALOG_URL", "http://127.0.0.1:8001")


def remote_price(sku, timeout=5):
    """Price of one SKU from the catalog service. Raises urllib.error.HTTPError (404) for an unknown SKU."""
    with urllib.request.urlopen("%s/price/%s" % (CATALOG_URL, sku), timeout=timeout) as resp:
        return float(json.loads(resp.read())["price"])


def remote_line_total(sku, qty):
    return remote_price(sku) * qty
