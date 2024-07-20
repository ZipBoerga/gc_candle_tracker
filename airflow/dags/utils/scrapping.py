import re
from typing import Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def _get_ingredients(url: str, soup) -> Optional[list[str]]:
    url_regex = r'\S*\?a=[0-9]+&lang=\S*'

    is_old_formatting = bool(re.fullmatch(url_regex, url))

    if is_old_formatting:
        return None

    ingr_table = soup.find('tbody')
    rows = ingr_table.find_all('tr')

    ingredients = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) == 2:
            level_ingredients = cells[1].text.strip().split(',')
            for i, ingredient in enumerate(level_ingredients):
                level_ingredients[i] = ingredient.strip()
            ingredients = ingredients + level_ingredients
    return ingredients


def get_candle_details(url: str) -> Optional[dict]:
    try:
        cookies = {'oss_country': 'GR', 'JTLSHOP': 'f5a6b3ed9cdca67475b65081793f61e9'}
        page = requests.get(url, cookies=cookies)
        soup = BeautifulSoup(page.content, 'html.parser')

        sku = soup.select_one('.product-sku span').text.strip()

        name = soup.find(class_='product-title has-border-bottom').text.strip()

        pic_element = soup.find(class_='square square-image js-gallery-images').find(
            'source'
        )
        pic_url = pic_element.attrs['srcset'].split(',')[-1].strip().split(' ')[0]

        ingredients = _get_ingredients(url, soup)

        price = soup.find(class_='range-price').text.strip().split(' ')[0]
        price = float(price.replace(',', '.'))

        return {
            'candle_id': sku,
            'url': url,
            'name': name,
            'picture_url': pic_url,
            'ingredients': ingredients,
            'price': price,
            'processing_date': int(datetime.now().timestamp())
        }
    except Exception as e:
        print(f'Error processing candle {url}: {e}')
        return None


def _get_urls_from_page(page) -> list[str]:
    urls: list[str] = []
    soup = BeautifulSoup(page.content, 'html.parser')
    href_blocks = soup.find_all(class_='d-block position-relative')
    for block in href_blocks:
        urls.append(block['href'])
    return urls


def get_candle_urls() -> list[str]:
    def is_first_page(_url):
        return not re.search(r'_s\d+$', _url)

    candle_urls: list[str] = []

    base_url = 'https://www.goosecreekcandle.de/3-Wick-Candles_s'
    index = 1
    is_first_iteration = True

    while True:
        url = f'{base_url}{index}'
        print(f'new iter {index} {url}')
        page = requests.get(url)

        if not is_first_iteration and is_first_page(page.url):
            return candle_urls

        candle_urls = candle_urls + _get_urls_from_page(page)
        index += 1
        is_first_iteration = False
