"""Compare product attribute coverage without treating price as assortment."""
import json
import os
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen

AMAZON_DATASET_ID = "gd_l7q7dkf244hwjntr0"


def compare_assortment(own_products, peer_products):
    def attributes(rows):
        return {key for row in rows for key, value in row.items() if key not in {"title", "asin", "url", "product_url"} and value not in (None, "", [], {})}
    own, peers = attributes(own_products), attributes(peer_products)
    all_keys = own | peers
    observed = lambda rows: {key: {"present": sum(row.get(key) not in (None, "", [], {}) for row in rows), "rate": round(sum(row.get(key) not in (None, "", [], {}) for row in rows) / len(rows), 3)} for key in sorted(all_keys)}
    return {"own_product_count": len(own_products), "peer_product_count": len(peer_products), "owned_only_attributes": sorted(own - peers), "peer_only_attributes": sorted(peers - own), "shared_attributes": sorted(own & peers), "observed_key_presence": {"own": observed(own_products), "peers": observed(peer_products)}, "decision_note": "Attribute lists indicate observed-key presence at least once, not meaningful catalog coverage. Per-cohort counts and rates are provided; this does not prove customer demand or product quality."}


def validate_cohorts(groups):
    for cohort in ("own", "peers"):
        urls = groups.get(cohort)
        if not isinstance(urls, list) or not 1 <= len(urls) <= 20:
            raise ValueError(f"Both cohorts must contain 1 to 20 product URLs; invalid {cohort} cohort")
        for url in urls:
            if not isinstance(url, str):
                raise ValueError(f"Every {cohort} product URL must be a string")
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.hostname not in {"amazon.com", "www.amazon.com"} or not ("/dp/" in parsed.path or "/gp/product/" in parsed.path):
                raise ValueError(f"Not a supported public Amazon product URL: {url}")


def collect_products(urls, api_key):
    if not 1 <= len(urls) <= 20:
        raise ValueError("Synchronous collection accepts 1 to 20 product URLs")
    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in {"amazon.com", "www.amazon.com"} or not ("/dp/" in parsed.path or "/gp/product/" in parsed.path):
            raise ValueError(f"Not a supported public Amazon product URL: {url}")
    request = Request(f"https://api.brightdata.com/datasets/v3/scrape?dataset_id={AMAZON_DATASET_ID}&format=json", data=json.dumps([{"url": url} for url in urls]).encode(), headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    with urlopen(request, timeout=65) as response:
        if getattr(response, "status", 200) == 202:
            raise RuntimeError("Bright Data returned an async snapshot; use the documented async workflow for this batch")
        return json.load(response)


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 tool.py SAMPLE.json | --live URLS.json")
    if sys.argv[1] == "--live":
        if len(sys.argv) != 3 or not os.getenv("BRIGHT_DATA_API_KEY"):
            raise SystemExit("Set BRIGHT_DATA_API_KEY and provide a JSON file with own and peers URL arrays")
        with open(sys.argv[2], encoding="utf-8") as source:
            groups = json.load(source)
        try:
            validate_cohorts(groups)
        except ValueError as error:
            raise SystemExit(str(error)) from error
        own = collect_products(groups["own"], os.environ["BRIGHT_DATA_API_KEY"])
        peers = collect_products(groups.get("peers", []), os.environ["BRIGHT_DATA_API_KEY"])
    else:
        with open(sys.argv[1], encoding="utf-8") as source:
            records = json.load(source)
        own, peers = records.get("own", []), records.get("peers", [])
    print(json.dumps(compare_assortment(own, peers), indent=2))


if __name__ == "__main__":
    main()
