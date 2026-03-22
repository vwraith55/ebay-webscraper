# eBay Scraper

## What it does

`ebay-dl.py` is a Python script that scrapes eBay search results and saves the data to a JSON file (or CSV with an optional flag). It takes a search term from the command line, fetches the first 10 pages of results, and extracts key information about each listing.

For each item, the script collects:

- **name** – the title of the listing
- **price** – item price in cents (integer)
- **status** – condition of the item (e.g. `"Brand New"`, `"Pre-owned"`, `"Refurbished"`)
- **shipping** – shipping cost in cents (`0` if free shipping)
- **freereturns** – whether the item has free returns (`true`/`false`)
- **items_sold** – number of units sold (integer)

If a field is not available for a particular item, its value is stored as `null`.

## Requirements

Install the required dependencies:

```bash
pip install playwright beautifulsoup4
playwright install firefox
```
Note: This script uses playwright instead of requests to download pages, as eBay's bot detection blocked requests calls.

## How to run

Pass your search term as a positional argument. Wrap multi-word search terms in quotes.

The following commands generate the three JSON files in this repo:

```bash
python3 ebay-dl.py 'laptop'
```

```bash
python3 ebay-dl.py 'water bottle'
```

```bash
python3 ebay-dl.py 'headphones'
```

These generate `laptop.json`, `water_bottle.json`, and `headphones.json`.

## Output format

```json
[
  {
    "name": "Apple MacBook Air 13 Laptop - MD760LL/A",
    "price": 18999,
    "status": "Pre-owned",
    "shipping": 0,
    "freereturns": true,
    "items_sold": 23
  }
]
```

## CSV option (extra credit)

Add the `--csv` flag to save results as a CSV file instead of JSON:

```bash
python3 ebay-dl.py 'laptop' --csv
```

```bash
python3 ebay-dl.py 'water bottle' --csv
```

```bash
python3 ebay-dl.py 'headphones' --csv
```

These generate `laptop.csv`, `water_bottle.csv`, and `headphones.csv`.

## Course project

[CMC CSCI040 Project 02 Webscraping](https://github.com/mikeizbicki/cmc-csci040/tree/2026spring/project_02_webscraping)