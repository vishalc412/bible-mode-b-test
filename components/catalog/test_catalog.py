import ssl
import unittest
from unittest.mock import patch

from components.catalog import catalog


class CatalogTest(unittest.TestCase):
    def test_price_of_known_sku(self):
        self.assertEqual(catalog.price_of("SKU-1"), 24.0)

    def test_supplier_feed_uses_verified_https(self):
        with patch("components.catalog.catalog.urllib.request.urlopen") as urlopen:
            response = urlopen.return_value.__enter__.return_value
            response.read.return_value = b'{"products": []}'

            self.assertEqual(catalog.fetch_supplier_feed(), {"products": []})

        args, kwargs = urlopen.call_args
        self.assertEqual(args[0], "https://feeds.supplier-one.example.com/v2/products.json")
        self.assertEqual(kwargs["timeout"], 10)
        self.assertTrue(kwargs["context"].check_hostname)
        self.assertEqual(kwargs["context"].verify_mode, ssl.CERT_REQUIRED)


if __name__ == "__main__":
    unittest.main()
