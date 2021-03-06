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
            'ExternalStorageDrive',
            'SolidStateDrive',
            'UsbFlashDrive',
            'MemoryCard',
            'Ram',
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        category_paths = [
            ['lacie-chile/discos-externos', 'ExternalStorageDrive'],
            ['lacie-chile/discos-portatiles', 'ExternalStorageDrive'],
            ['lacie-chile/discos-thunderbolt', 'ExternalStorageDrive'],
            ['accesorios-mac-pc/discos-duros-externos',
             'ExternalStorageDrive'],
            ['accesorios-mac-pc/discos-duros-portatiles',
             'ExternalStorageDrive'],
            ['hardware-mac-pc/discos-duros-notebook-sata-2.5',
             'SolidStateDrive'],
            ['hardware-mac-pc/discos-duros-ssd-sata-2.5', 'SolidStateDrive'],
            ['hardware-mac-pc/SSD-M2-PCIe-NVMe', 'SolidStateDrive'],
            ['hardware-mac-pc/SSD-M2-SATA', 'SolidStateDrive'],
            ['hardware-mac-pc/SSD-mSATA', 'SolidStateDrive'],
            ['hardware-mac-pc/memorias-ram', 'Ram'],
            ['hardware-mac-pc/Tarjetas-Expansion-Flashdrive-SDCard-y-SSD-'
             'para-Apple-Mac', 'MemoryCard'],
        ]

        product_urls = []
        session = session_with_proxy(extra_args)

        for category_path, local_category in category_paths:
            if local_category != category:
                continue

            category_url = 'https://www.globalmac.cl/' + category_path
            print(category_url)
            soup = BeautifulSoup(session.get(category_url).text,
                                 'html.parser')

            items = soup.findAll('div', 'product-layout')

            for item in items:
                product_urls.append(item.find('a')['href'])

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        print(url)
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text,
                             'html.parser')

        name = soup.find('title').text.strip()
        sku = soup.find('meta', {'itemprop': 'model'})['content']

        description = html_to_markdown(
            str(soup.find('div', {'id': 'tab-description'})))
        pictures_container = soup.find('ul', 'thumbnails')

        if pictures_container:
            picture_urls = [tag['href'] for tag in pictures_container.findAll(
                'a', 'thumbnail') if tag['href']]
        else:
            picture_urls = None

        if soup.find('link', {'itemprop': 'availability'})['href'] == \
                'http://schema.org/InStock':
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
