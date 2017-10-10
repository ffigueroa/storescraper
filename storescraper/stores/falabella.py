import json
import urllib
from collections import OrderedDict
from decimal import Decimal

import re

import requests
from bs4 import BeautifulSoup

from storescraper.product import Product
from storescraper.store import Store
from storescraper.utils import remove_words, html_to_markdown


class Falabella(Store):
    @classmethod
    def categories(cls):
        return [
            'Notebook',
            'Television',
            'Tablet',
            'Refrigerator',
            'Printer',
            'Oven',
            'VacuumCleaner',
            'WashingMachine',
            'Cell',
            'Camera',
            'StereoSystem',
            'OpticalDiskPlayer',
            'HomeTheater',
            'ExternalStorageDrive',
            'UsbFlashDrive',
            'MemoryCard',
            'Projector',
            'VideoGameConsole',
            'CellAccesory',
            'AllInOne',
            'AirConditioner',
            'Monitor',
            'WaterHeater',
            'SolidStateDrive',
            'Mouse',
            'SpaceHeater',
        ]

    @classmethod
    def discover_urls_for_category(cls, category, extra_args=None):
        url_paths = [
            ['cat5860031/Notebooks-Convencionales', 'Notebook'],
            ['cat2028/Notebooks-Gamers', 'Notebook'],
            ['cat2450060/Notebooks-2-en-1', 'Notebook'],
            ['cat5860030/MacBooks', 'Notebook'],
            ['cat70043/Televisores', 'Television'],
            ['cat3118/Tablet', 'Tablet'],
            ['cat4074/No-Frost', 'Refrigerator'],
            ['cat4091/Side-by-Side', 'Refrigerator'],
            ['cat4036/Frio-Directo', 'Refrigerator'],
            ['cat4048/Freezer', 'Refrigerator'],
            ['cat4049/Frigobar', 'Refrigerator'],
            ['cat1840004/Cavas-de-Vino', 'Refrigerator'],
            ['cat2049/Impresoras', 'Printer'],
            ['cat3151/Microondas', 'Oven'],
            ['cat3114/Hornos-Electricos', 'Oven'],
            ['cat3025/Aspiradoras-y-Enceradoras', 'VacuumCleaner'],
            ['cat4060/Lavadoras', 'WashingMachine'],
            ['cat1700002/Lavadora-Secadora', 'WashingMachine'],
            ['cat4088/Secadoras', 'WashingMachine'],
            ['cat1280018/Celulares-Basicos', 'Cell'],
            ['cat720161/Smartphones', 'Cell'],
            ['cat70028/Camaras-Compactas', 'Camera'],
            ['cat70029/Camaras-Semiprofesionales', 'Camera'],
            ['cat3091/Equipos-de-Musica', 'StereoSystem'],
            ['cat3171/Parlantes-y-Docking', 'StereoSystem'],
            ['cat2032/DVD-y-Blu-Ray', 'OpticalDiskPlayer'],
            ['cat2045/Home-Theater', 'HomeTheater'],
            ['cat3087/Discos-duros', 'ExternalStorageDrive'],
            ['cat3177/Pendrives', 'UsbFlashDrive'],
            ['cat70037/Tarjetas-de-Memoria', 'MemoryCard'],
            ['cat2070/Proyectores', 'Projector'],
            ['cat3770004/Consolas', 'VideoGameConsole'],
            ['cat40051/All-In-One', 'AllInOne'],
            ['cat7830015/Portatiles', 'AirConditioner'],
            ['cat2062/Monitores', 'Monitor'],
            ['cat2013/Calefont-y-Termos', 'WaterHeater'],
            ['cat3155/Mouse', 'Mouse'],
            ['cat3097/Estufas', 'SpaceHeater'],
            ['cat4290063/SmartWatch', 'Smartwatch'],
        ]

        session = requests.Session()
        session.headers.update({
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en,en-US;q=0.8,es;q=0.6',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'DNT': '1',
            'Host': 'www.falabella.com',
            'Referer': 'http://www.falabella.com/falabella-cl/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/'
                          '537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 '
                          'Safari/537.36'
        })
        session.get('http://www.falabella.com/falabella-cl/')
        session.get('http://www.falabella.com/falabella-cl/'
                    'includes/ajaxFirstNameAndCartQuantity.jsp')
        discovered_urls = []

        for url_path, local_category in url_paths:
            if local_category != category:
                continue

            sorters = [
                None,  # No sorting
                1,  # Precio menor a mayor
                2,  # Precio mayor a menor
                3,  # Marca
                4,  # Destacados
                5,  # Recomendados
                6,  # Mejor evaluados
                7,  # Nuevos productos
            ]

            # Falabella tends to... fail... so try different requests using
            # the different available sorters... twice... just in case.
            category_product_urls = None

            for i in range(2 * len(sorters)):
                try:
                    category_product_urls = cls._get_category_product_urls(
                        session,
                        url_path,
                        sorters[i % len(sorters)]
                    )
                    break
                except Exception:
                    continue

            if not category_product_urls:
                raise Exception('Category error: ' + url_path)

            discovered_urls.extend(category_product_urls)

        return discovered_urls

    @classmethod
    def products_for_url(cls, url, category=None, extra_args=None):
        session = requests.Session()
        content = session.get(url).text.replace('&#10;', '')

        soup = BeautifulSoup(content, 'html.parser')

        panels = ['fb-product-information__product-information-tab',
                  'fb-product-information__specification']

        description = ''

        for panel in panels:
            description += html_to_markdown(str(soup.find('div', panel))) + \
                           '\n\n'

        raw_json_data = re.search('var fbra_browseMainProductConfig = (.+);\r',
                                  content)

        if not raw_json_data:
            return []

        product_data = json.loads(raw_json_data.groups()[0])

        brand = product_data['state']['product']['brand']
        model = product_data['state']['product']['displayName']
        full_name = '{} {}'.format(brand, model)

        global_id = product_data['state']['product']['id']
        media_asset_url = product_data['endPoints']['mediaAssetUrl']['path']

        pictures_resource_url = 'http://falabella.scene7.com/is/image/' \
                                'Falabella/{}?req=set,json'.format(global_id)
        pictures_json = json.loads(
            re.search(r's7jsonResponse\((.+),""\);',
                      session.get(pictures_resource_url).text).groups()[0])
        picture_urls = []

        picture_entries = pictures_json['set']['item']
        if not isinstance(picture_entries, list):
            picture_entries = [picture_entries]

        for picture_entry in picture_entries:
            picture_url = '{}{}?scl=1.0'.format(media_asset_url,
                                                picture_entry['i']['n'])
            picture_urls.append(picture_url)

        products = []
        for model in product_data['state']['product']['skus']:
            if 'stockAvailable' not in model:
                continue

            sku = model['skuId']

            prices = {e['type']: e for e in model['price']}

            lookup_field = 'originalPrice'
            if lookup_field not in prices[3]:
                lookup_field = 'formattedLowestPrice'

            normal_price = Decimal(remove_words(prices[3][lookup_field]))

            if 1 in prices:
                lookup_field = 'originalPrice'
                if lookup_field not in prices[1]:
                    lookup_field = 'formattedLowestPrice'
                offer_price = Decimal(
                    remove_words(prices[1][lookup_field]))
            else:
                offer_price = normal_price

            stock = model['stockAvailable']

            p = Product(
                full_name,
                cls.__name__,
                category,
                url,
                url,
                sku,
                stock,
                normal_price,
                offer_price,
                'CLP',
                sku=sku,
                description=description,
                cell_plan_name=None,
                cell_monthly_payment=None,
                picture_urls=picture_urls
            )

            products.append(p)

        return products

    @classmethod
    def _get_category_product_urls(cls, session, url_path, sorter):
        discovered_urls = []
        query_args = OrderedDict([
            ('currentPage', 1),
            # ('sortBy', sorter),
            ('navState', "/category/{}?sortBy={}".format(url_path, sorter))])

        if not sorter:
            query_args['navState'] = "/category/{}".format(url_path)

        page = 1

        while True:
            if page > 30:
                raise Exception('Page overflow: ' + url_path)

            res = None

            error_count = 0
            while res is None or 'errors' in res:
                error_count += 1
                if error_count > 10:
                    raise Exception('Error threshold exceeded: ' + url_path)
                query_args['currentPage'] = page
                pag_url = 'http://www.falabella.com/rest/model/' \
                          'falabella/rest/browse/BrowseActor/' \
                          'get-product-record-list?{}'.format(
                            urllib.parse.quote(json.dumps(
                                query_args, separators=(',', ':')), safe=''))

                res = json.loads(
                    session.get(pag_url).content.decode('utf-8'))

            if not res['state']['resultList'] and page == 1:
                raise Exception('Empty category path: ' + url_path)

            for product_entry in res['state']['resultList']:
                product_id = product_entry['productId'].strip()
                product_url = \
                    'http://www.falabella.com/falabella-cl/product/{}/' \
                    ''.format(product_id)
                discovered_urls.append(product_url)

            if res['state']['pagesTotal'] == page:
                break

            page += 1

        return discovered_urls