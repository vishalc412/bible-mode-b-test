import json
import os
import threading
import unittest
import urllib.error
import urllib.request

from components.catalog import service
from components.orders import catalog_client


class CatalogClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = service.make_server("127.0.0.1", 0)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = "http://127.0.0.1:%d" % cls.server.server_address[1]
        cls.saved = os.environ.get("CATALOG_URL")
        os.environ["CATALOG_URL"] = cls.base

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        if cls.saved is None:
            os.environ.pop("CATALOG_URL", None)
        else:
            os.environ["CATALOG_URL"] = cls.saved

    def get(self, path):
        try:
            with urllib.request.urlopen(self.base + path, timeout=5) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read())

    def test_remote_price(self):
        self.assertEqual(catalog_client.remote_price("SKU-1"), 24.0)

    def test_remote_line_total(self):
        self.assertEqual(catalog_client.remote_line_total("SKU-3", 2), 12.0)

    def test_quantity_must_be_positive(self):
        with self.assertRaises(ValueError):
            catalog_client.remote_line_total("SKU-3", 0)

    def test_unknown_sku(self):
        with self.assertRaises(urllib.error.HTTPError):
            catalog_client.remote_price("SKU-9")

    def test_odd_skus_are_quoted_not_misrouted(self):
        for sku in ("SKU-1#f", "SKU-1?x=1", "SKU 1", "SK\u00dc", "SKU-1/../health"):
            with self.assertRaises(urllib.error.HTTPError, msg=sku):
                catalog_client.remote_price(sku)

    def test_query_string_ignored_by_server(self):
        self.assertEqual(self.get("/health?x=1"), (200, {"status": "ok"}))
        self.assertEqual(self.get("/price/SKU-1?x=1")[1]["price"], 24.0)

    def test_percent_encoded_sku_decoded(self):
        code, body = self.get("/price/SKU%2D1")
        self.assertEqual((code, body["sku"]), (200, "SKU-1"))


if __name__ == "__main__":
    unittest.main()
