from bs4 import BeautifulSoup
from decimal import Decimal

from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import html_to_markdown, session_with_proxy


class BestBuyMexico(Store):
    @classmethod
    def categories(cls):
        return [
            'ExternalStorageDrive',
            'MemoryCard',
            'UsbFlashDrive',
            'SolidStateDrive',
            'StorageDrive',
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        category_paths = [
            ['computadoras/gaming.html?comp_compu_acc_tipo_dispositivo='
             'Unidades+de+estado+sólido', 'SolidStateDrive'],
            ['computadoras/discos-duros-y-almacenamiento.html?'
             'comp_compu_acc_tipo_dispositivo=Discos+Duros',
             'ExternalStorageDrive'],
            ['computadoras/discos-duros-y-almacenamiento.html?'
             'comp_compu_acc_tipo_dispositivo=Micro+SD', 'MemoryCard'],
            ['computadoras/discos-duros-y-almacenamiento.html?'
             'comp_compu_acc_tipo_dispositivo=Unidades+de+estado+sólido',
             'SolidStateDrive'],
            ['computadoras/discos-duros-y-almacenamiento.html?'
             'comp_compu_acc_tipo_dispositivo=USB',
             'UsbFlashDrive'],
            ['tablets-y-celulares/accesorios-para-celulares.html?'
             'comp_compu_acc_tipo_dispositivo=Tarjetas+de+memoria',
             'MemoryCard'],
            ['tablets-y-celulares/accesorios-para-tablets.html?'
             'comp_compu_acc_tipo_dispositivo=Tarjetas+de+memoria',
             'MemoryCard'],
        ]

        product_urls = []

        session = session_with_proxy(extra_args)

        for category_path, local_category in category_paths:
            if local_category != category:
                continue

            category_url = 'http://www.bestbuy.com.mx/productos/{}&limit=all' \
                           ''.format(category_path)

            soup = BeautifulSoup(session.get(category_url).text,
                                 'html.parser')

            product_cells = soup.findAll('li', 'item')

            if not product_cells:
                raise Exception('No products found: {}'.format(category_url))

            for product_cell in product_cells:
                product_url = product_cell.find('a')['href']
                product_urls.append(product_url)

        return product_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        session = session_with_proxy(extra_args)
        soup = BeautifulSoup(session.get(url).text, 'html.parser')

        name = soup.find('h1').text.strip()

        pricing_tag = soup.find(
            'script', {'src': 'http://media.flixfacts.com/js/loader.js'})

        sku = pricing_tag['data-flix-sku'].strip()
        part_number = pricing_tag['data-flix-mpn'].strip()
        ean = pricing_tag['data-flix-ean'].strip()

        if len(ean) == 12:
            ean = '0' + ean

        normal_price = Decimal(soup.find('span', 'price').text.replace(
            u'$\xa0', '').replace(',', ''))

        offer_price = normal_price

        description = html_to_markdown(
            str(soup.find('div', {'id': 'tabcnt_description'})))

        picture_tags = soup.find('div', 'product-img-box').findAll('img')
        picture_urls = [picture['src'] for picture in picture_tags]

        p = Product(
            name,
            cls.__name__,
            category,
            url,
            url,
            sku,
            -1,
            normal_price,
            offer_price,
            'MXN',
            sku=sku,
            part_number=part_number,
            ean=ean,
            description=description,
            picture_urls=picture_urls
        )

        return [p]