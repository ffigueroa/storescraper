from bs4 import BeautifulSoup
from decimal import Decimal

from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import session_with_proxy, remove_words, \
    html_to_markdown


class GlobalMac(Store):
    @classmethod
    def categories(cls):
        return [
            'Notebook',
            'StorageDrive',
            'SolidStateDrive',
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        category_paths = [
            # ['apple-chile/macbook-air', 'Notebook'],
            # ['apple-chile/macbook-pro', 'Notebook'],
            ['hardware-mac-pc/discos-duros-notebook-sata-2.5', 'StorageDrive'],
            # ['hardware-mac-pc/discos-duros-sata-3.5', 'StorageDrive'],
            ['hardware-mac-pc/discos-duros-ssd-sata-2.5', 'SolidStateDrive'],
        ]

        product_urls = []
        session = session_with_proxy(extra_args)

        for category_path, local_category in category_paths:
            if local_category != category:
                continue

            category_url = 'http://www.globalmac.cl/' + category_path
            soup = BeautifulSoup(session.get(category_url).text, 'html.parser')

            items = soup.findAll('div', 'product-layout')

            for item in items:
                product_urls.append(item.find('a')['href'])

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, 'html.parser')

        name = soup.find('title').text.strip()
        sku = soup.find('meta', {'itemprop': 'model'})['content']

        description = html_to_markdown(
            str(soup.find('div', {'id': 'tab-description'})))
        picture_urls = [tag['href'] for tag in soup.find(
            'ul', 'thumbnails').findAll('a', 'thumbnail')]

        if soup.find('link', {'itemprop': 'http://schema.org/InStock'}):
            stock = -1
        else:
            stock = 0

        price = soup.find('meta', {'itemprop': 'price'})['content']
        price = Decimal(remove_words(price))

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            sku,
            stock,
            price,
            price,
            'CLP',
            sku=sku,
            part_number=sku,
            description=description,
            picture_urls=picture_urls
        )

        return [p]
