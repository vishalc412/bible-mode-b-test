import ssl
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import HTTPSHandler, Request

from components.catalog import catalog


class CatalogTest(unittest.TestCase):
    def test_price_of_known_sku(self):
        self.assertEqual(catalog.price_of("SKU-1"), 24.0)

    def test_supplier_feed_uses_verified_https(self):
        with patch("components.catalog.catalog.urllib.request.build_opener") as build_opener:
            response = build_opener.return_value.open.return_value.__enter__.return_value
            response.read.return_value = b'{"products": []}'

            self.assertEqual(catalog.fetch_supplier_feed(), {"products": []})

        build_opener.assert_called_once()
        redirect_handler, https_handler = build_opener.call_args.args
        self.assertIsInstance(redirect_handler, catalog.NoHTTPRedirectHandler)
        self.assertIsInstance(https_handler, HTTPSHandler)
        context = https_handler._context
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)
        build_opener.return_value.open.assert_called_once_with(
            "https://feeds.supplier-one.example.com/v2/products.json", timeout=10
        )

    def test_supplier_feed_rejects_redirect_to_http(self):
        handler = catalog.NoHTTPRedirectHandler()
        request = Request("https://feeds.supplier-one.example.com/v2/products.json")

        with self.assertRaises(HTTPError):
            handler.redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "http://feeds.supplier-one.example.com/v2/products.json",
            )


if __name__ == "__main__":
    unittest.main()
