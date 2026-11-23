"""Orders' client for the catalog HTTP API (components/catalog/service.py).

Orders running as its own service reads prices over the network instead of importing the catalog.
CATALOG_URL points at the catalog service; today the call is plain HTTP.
"""
import json
import os
import urllib.parse
import urllib.request

DEFAULT_CATALOG_URL = "http://127.0.0.1:8001"


def catalog_url():
    """The catalog service's base URL, read on every call so a change of CATALOG_URL takes effect."""
    return os.environ.get("CATALOG_URL", DEFAULT_CATALOG_URL).rstrip("/")


def remote_price(sku, timeout=5):
    """Price of one SKU from the catalog service. Raises urllib.error.HTTPError (404) for an unknown SKU."""
    url = "%s/price/%s" % (catalog_url(), urllib.parse.quote(sku, safe=""))
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return float(json.loads(resp.read())["price"])


def remote_line_total(sku, qty):
    if qty <= 0:
        raise ValueError("quantity must be positive")
    return remote_price(sku) * qty
