import threading
import unittest
import urllib.error

from components.catalog import service
from components.orders import catalog_client


class CatalogClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = service.make_server("127.0.0.1", 0)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        catalog_client.CATALOG_URL = "http://127.0.0.1:%d" % cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_remote_price(self):
        self.assertEqual(catalog_client.remote_price("SKU-1"), 24.0)

    def test_remote_line_total(self):
        self.assertEqual(catalog_client.remote_line_total("SKU-3", 2), 12.0)

    def test_unknown_sku(self):
        with self.assertRaises(urllib.error.HTTPError):
            catalog_client.remote_price("SKU-9")


if __name__ == "__main__":
    unittest.main()
