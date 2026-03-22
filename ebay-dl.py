import argparse
import csv
import json
import re
import time
import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
 
 
def parse_itemssold(text):
    '''
    >>> parse_itemssold('38 sold')
    38
    >>> parse_itemssold('14 watchers')
    0
    >>> parse_itemssold('Almost gone')
    0
    '''
    if not text:
        return 0
    m = re.search(r'([\d,]+)\s+sold', text, re.I)
    if m:
        return int(m.group(1).replace(',', ''))
    return 0
 
 
def parse_shipping_price(text):
    '''
    >>> parse_shipping_price('Free shipping')
    0
    >>> parse_shipping_price('+$90.00 shipping')
    9000
    '''
    if not text:
        return None
    if 'free' in text.lower():
        return 0
    m = re.search(r'\$[\d,]+\.?\d*', text)
    if m:
        price_clean = m.group().replace('$', '').replace(',', '')
        return int(float(price_clean) * 100)
    return None
 
 
def parse_price(text):
    '''
    >>> parse_price('$825.00')
    82500
    >>> parse_price('$499.99')
    49999
    >>> parse_price('$1,099.99')
    109999
    >>> parse_price('$31.70 to $266.83')
    3170
    '''
    if not text:
        return None
    if 'to' in text:
        text = text.split(' to ')[0]
    m = re.search(r'\$[\d,]+\.?\d*', text)
    if m:
        price_clean = m.group().replace('$', '').replace(',', '')
        return int(float(price_clean) * 100)
    return None
 
 
def download_html(url):
    """Use Playwright to fetch a fully rendered eBay page."""
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = context.new_page()
        page.goto(url)
        # Wait until actual listing cards appear — much more reliable than networkidle
        page.wait_for_selector("li.s-card", timeout=15000)
        html = page.content()
        browser.close()
    return html
 
 
if __name__ == '__main__':
 
    parser = argparse.ArgumentParser(description='Download information from eBay and convert to JSON.')
    parser.add_argument('search_term')
    parser.add_argument('--num_pages', default=10)
    parser.add_argument('--csv', action='store_true')
    args = parser.parse_args()
 
    items = []
 
    for page_number in range(1, int(args.num_pages) + 1):
 
        url = 'https://www.ebay.com/sch/i.html?_nkw='
        url += args.search_term.replace(' ', '+')
        url += '&_sacat=0&_from=R40&_pgn='
        url += str(page_number)
        url += '&rt=nc'
 
        print(f'Fetching page {page_number}: {url}')
 
        try:
            html = download_html(url)
        except Exception as e:
            print(f'  Could not load page: {e}. Skipping.')
            continue
 
        blocked = "Pardon Our Interruption" in html
        print("blocked?", blocked)
        if blocked:
            continue
 
        soup = BeautifulSoup(html, 'html.parser')
        tags_items = soup.select('li.s-card')
        print(f'  Found {len(tags_items)} listings')
 
        for tag_item in tags_items:
 
            # name
            name = None
            tag_name = tag_item.select_one('.s-card__title')
            if tag_name:
                title = tag_name.get_text(strip=True)
                if title.lower() == 'shop on ebay':
                    continue
                name = title
            if name is None:
                continue
 
            # price
            price = None
            tag_price = tag_item.select_one('.s-card__price')
            if tag_price:
                price = parse_price(tag_price.get_text(strip=True))
 
            # status
            status = None
            tag_status = tag_item.select_one('.s-card__subtitle')
            if tag_status:
                status = tag_status.get_text(strip=True)
 
            # shipping + free returns
            full_text = tag_item.get_text(' ', strip=True)
 
            shipping = None
            for chunk in full_text.split('  '):
                if 'shipping' in chunk.lower() or 'delivery' in chunk.lower():
                    shipping = parse_shipping_price(chunk)
                    break
 
            free_returns = 'free return' in full_text.lower()
 
            # items sold
            items_sold = parse_itemssold(full_text)
            if items_sold == 0:
                items_sold = None
 
            item = {
                'name': name,
                'price': price,
                'status': status,
                'shipping': shipping,
                'free_returns': free_returns,
                'items_sold': items_sold,
            }
            items.append(item)
 
        # polite delay between pages
        if page_number < int(args.num_pages):
            delay = random.uniform(2, 5)
            print(f'  Waiting {delay:.1f}s...')
            time.sleep(delay)
 
    print(f'\nTotal items collected: {len(items)}')
 
    safe_term = args.search_term.replace(' ', '_')
 
    if args.csv:
        filename = safe_term + '.csv'
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)
        print(f'Saved to {filename}')
    else:
        filename = safe_term + '.json'
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(items, f, indent=2)
        print(f'Saved to {filename}')
 