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

    def test_live_main_validates_both_cohorts_before_any_request(self):
        import json
        import os
        import tempfile
        from unittest.mock import patch
        from tool import main
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as source:
            json.dump({"own": ["https://www.amazon.com/dp/B000000001"], "peers": []}, source)
            source.flush()
            with patch.dict(os.environ, {"BRIGHT_DATA_API_KEY": "test-key"}), patch("sys.argv", ["tool.py", "--live", source.name]), patch("tool.urlopen") as mocked:
                with self.assertRaisesRegex(SystemExit, "Both cohorts"):
                    main()
                mocked.assert_not_called()

    def test_observed_attribute_key_counts_are_reported_per_cohort(self):
        result = compare_assortment([{"color": "blue"}, {}], [{"color": "red"}])
        self.assertEqual(result["observed_key_presence"]["own"]["color"], {"present": 1, "rate": 0.5})
        self.assertEqual(result["observed_key_presence"]["peers"]["color"], {"present": 1, "rate": 1.0})

    def test_live_cli_failure_returns_structured_nonretryable_error(self):
        import json
        import os
        import tempfile
        from contextlib import redirect_stderr
        from io import StringIO
        from urllib.error import URLError
        from tool import main
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as source:
            json.dump({"own": ["https://www.amazon.com/dp/B000000001"], "peers": ["https://www.amazon.com/dp/B000000002"]}, source)
            source.flush()
            with patch.dict(os.environ, {"BRIGHT_DATA_API_KEY": "secret-token"}), patch("sys.argv", ["tool.py", "--live", source.name]), patch("tool.collect_products", side_effect=URLError("secret-token")), redirect_stderr(StringIO()) as error:
                with self.assertRaises(SystemExit) as exit_error:
                    main()
        payload = json.loads(error.getvalue())
        self.assertEqual(exit_error.exception.code, 1)
        self.assertFalse(payload["error"]["retryable"])
        self.assertNotIn("secret-token", error.getvalue())


if __name__ == "__main__":
    unittest.main()
