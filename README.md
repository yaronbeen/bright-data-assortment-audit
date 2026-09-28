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

Bright Data documents Amazon product records with title, ASIN, brand, price, rating, review count, seller, and availability. This adapter uses the documented product dataset `gd_l7q7dkf244hwjntr0`, synchronous `POST /datasets/v3/scrape`, and the 20-URL request bound. References: [Amazon Scraper API](https://docs.brightdata.com/products/scrapers/amazon/introduction.md), [quickstart](https://docs.brightdata.com/products/scrapers/amazon/quickstart.md), [product response schema](https://docs.brightdata.com/api-reference/scrapers/e-commerce-apis/amazon-products-collect-by-url).

## Run

```bash
python3 tool.py sample.json
printf '{"own":["https://www.amazon.com/dp/B000000001"],"peers":["https://www.amazon.com/dp/B000000002"]}\n' > urls.json
BRIGHT_DATA_API_KEY="your-key" python3 tool.py --live urls.json
python3 -m unittest -v
```

The live command collects URLs from the `own` and `peers` arrays separately, then compares the two returned record sets. This intentionally makes group assignment explicit. Each non-empty group is one request. Live API calls may incur charges; a 202 async response is reported rather than silently polled.

## Outputs

JSON reports sample sizes and observed attribute keys unique to either sample or shared by both. Price fields are not used to generate a price delta. Empty fields are ignored; values are not interpreted semantically.

## Differentiation

Existing account projects include a competitor pricing tracker and the WIP Amazon price/rating and Q&A concepts. This audit deliberately excludes prices, ratings, reviews, and rank changes. It answers a catalog-taxonomy question: which attributes are represented in one supplied product sample but not the other? It does not discover leads or predict sales.

## FAQ

**Does it recommend which product attributes to add?** No. It highlights observed differences for human evaluation.

**Can it process more than 20 URLs?** The documented synchronous endpoint is capped at 20. This demo fails clearly rather than quietly launching an async job; use Bright Data's documented async workflow for larger collections.

**Can I run without credentials?** Yes. The synthetic fixture and unit tests are offline.

## Compliance and limitations

Use public product URLs for legitimate market research and follow Amazon, Bright Data, and applicable legal requirements. Returned catalog attributes may be incomplete or change between runs. Data is not cached or retained by this script. Do not make product or investment decisions from a small sample alone.

## Bright Data

Powered by [Bright Data Amazon Scraper API](https://brightdata.com/products/web-scraper/amazon). MIT licensed.
