# Bright Data Amazon Assortment Audit

Compare returned product attribute coverage between a merchant's own catalog sample and a small peer sample. The decision is which product attributes merit follow-up research or richer catalog content. This is not a price tracker, rating monitor, review miner, or demand forecast.

## Synthetic Example -> Decision

The fixture compares an invented 750ml blue bottle with an invented peer insulated bottle. The report identifies `capacity` as only observed in the own sample and `insulation` as only observed in the peer sample. A merchandising lead can check whether those attributes are relevant to their catalog taxonomy and product-page content. The output does not say customers prefer either feature.

## Workflow

1. Supply up to 20 public Amazon product URLs in each explicitly labeled cohort.
2. Collect structured product records with Bright Data's Amazon product dataset.
3. Compare which non-identity, non-URL attributes are observed in each cohort.
4. Verify any catalog follow-up against the source listing and the merchant's own taxonomy.

## Setup

Python 3.10+; standard library only.

```bash
cp .env.example .env
export BRIGHT_DATA_API_KEY="your-key"
```

Bright Data documents Amazon product records with title, ASIN, brand, price, rating, review count, seller, and availability. This adapter uses product dataset `gd_l7q7dkf244hwjntr0` and synchronous `POST /datasets/v3/scrape`. This tool imposes a 20-URL maximum per cohort; treat it as this tool's request bound unless the current source documentation confirms a platform-level cap. References: [Amazon Scraper API](https://docs.brightdata.com/products/scrapers/amazon/introduction.md), [quickstart](https://docs.brightdata.com/products/scrapers/amazon/quickstart.md), [product response schema](https://docs.brightdata.com/api-reference/scrapers/e-commerce-apis/amazon-products-collect-by-url).

## Run

```bash
python3 tool.py sample.json
printf '{"own":["https://www.amazon.com/dp/B000000001"],"peers":["https://www.amazon.com/dp/B000000002"]}\n' > urls.json
BRIGHT_DATA_API_KEY="your-key" python3 tool.py --live urls.json
python3 -m unittest -v
```

The live command validates that both cohorts contain 1-20 valid URLs before making any request, then collects the cohorts separately. This intentionally makes group assignment explicit. Each cohort is one request and may incur charges. A 202 async response is reported rather than silently polled. Requests are not automatically retried because a repeated billable POST may duplicate usage. If one cohort request fails, the CLI returns a structured error naming the failed cohort and exits 1; it does not emit partial comparison results or claim per-URL status because collection is submitted as a batch.

## Outputs

JSON reports sample sizes, observed attribute keys unique to either sample or shared by both, and per-cohort presence counts/rates for each key. The unique/shared lists mean only that a key was observed at least once in a cohort; they are not coverage, quality, or semantic-value assessments. Price fields are not used to generate a price delta. Empty fields are ignored; values are not interpreted semantically.

On live HTTP/network/API failure, the CLI writes a JSON object to stderr with an `error` containing a stable `code`, sanitized `message`, and `retryable: false`, then exits 1. Success JSON remains on stdout. No automatic retry is made.

## Differentiation

Existing account projects include a competitor pricing tracker and the WIP Amazon price/rating and Q&A concepts. This audit deliberately excludes prices, ratings, reviews, and rank changes. It answers a catalog-taxonomy question: which attributes are represented in one supplied product sample but not the other? It does not discover leads or predict sales.

## FAQ

**Does it recommend which product attributes to add?** No. It highlights observed differences for human evaluation.

**Can it process more than 20 URLs per cohort?** No. This tool enforces a 20-URL bound per cohort before making either request. It fails clearly rather than quietly launching an async job; use Bright Data's documented async workflow for larger collections.

**Can I run without credentials?** Yes. The synthetic fixture and unit tests are offline.

## Compliance and limitations

Use public product URLs for legitimate market research and follow Amazon, Bright Data, and applicable legal requirements. Returned catalog attributes may be incomplete or change between runs. Data is not cached or retained by this script. Do not make product or investment decisions from a small sample alone.

## Bright Data

Powered by [Bright Data Amazon Scraper API](https://brightdata.com/products/web-scraper/amazon). MIT licensed.
