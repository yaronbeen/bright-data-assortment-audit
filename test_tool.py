import unittest
from io import BytesIO
from unittest.mock import patch

from tool import compare_assortment


class AssortmentAuditTests(unittest.TestCase):
    def test_reports_owned_only_peer_only_and_shared_attributes(self):
        mine = [{"title": "Bottle", "brand": "Acme", "color": "blue", "size": "1L"}]
        peers = [{"title": "Bottle", "brand": "Acme", "color": "red", "material": "steel"}]
        result = compare_assortment(mine, peers)
        self.assertEqual(result["owned_only_attributes"], ["size"])
        self.assertEqual(result["peer_only_attributes"], ["material"])
        self.assertEqual(result["shared_attributes"], ["brand", "color"])

    def test_ignores_empty_values_and_handles_empty_inputs(self):
        result = compare_assortment([{"title": "A", "color": ""}], [])
        self.assertEqual(result["peer_only_attributes"], [])
        self.assertEqual(result["owned_only_attributes"], [])

    def test_live_collection_uses_documented_amazon_dataset_and_body(self):
        from tool import collect_products
        response = BytesIO(b'[]')
        with patch("tool.urlopen", return_value=response) as mocked:
            collect_products(["https://www.amazon.com/dp/B000000001"], "test-key")
        request = mocked.call_args.args[0]
        self.assertIn("dataset_id=gd_l7q7dkf244hwjntr0", request.full_url)
        self.assertIn(b'"url": "https://www.amazon.com/dp/B000000001"', request.data)

    def test_live_collection_rejects_over_limit_before_network(self):
        from tool import collect_products
        with patch("tool.urlopen") as mocked:
            with self.assertRaises(ValueError):
                collect_products(["https://www.amazon.com/dp/B000000001"] * 21, "test-key")
            mocked.assert_not_called()


if __name__ == "__main__":
    unittest.main()
