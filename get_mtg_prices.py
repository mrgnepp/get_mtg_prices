#! /usr/bin/python

import abc
import argparse
import locale
import re
import threading
import time

import requests
from bs4 import BeautifulSoup


class CardSite:
    # Abstract class
    abc.__metaclass__ = abc.ABCMeta

    def __init__(self, foil):
        self.selling_prices = []
        self.buying_prices = []

        self.url = ''
        self.sell_list_url = '/products/search?'
        self.buy_list_url = '/buylist/search?'

        self.foil = foil
        self.foil_append = ' - Foil'

    def get_prices(self, card_list, quality, is_store_buying):
        begin_time = time.perf_counter()

        if is_store_buying:
            self.url = self.base_url + self.buy_list_url
        else:
            self.url = self.base_url + self.sell_list_url

        for card in card_list:
            card_prices = []
            if self.foil:
                card = f'{card}{self.foil_append}'

            response = requests.get(url=self.url, params={self.url_arg: card})

            print(f'Searching... {response.url}')
            if response.status_code == requests.codes.ok:
                soup = BeautifulSoup(response.text, 'html.parser')

                # DEBUG
                # with open('soup.html', 'wb') as file:
                #     file.write(soup.prettify('utf-8'))

                # Ensure we grab the correct card
                elements = soup.find_all(self.card_name_element, string=re.compile(f'^{card}$', re.I))
                for element in elements:
                    # Create new soup to restrict search for card
                    card_soup = BeautifulSoup(str(self.get_card_element(element)), 'html.parser')

                    # DEBUG
                    # with open('card_soup.html', 'wb') as file:
                    #     file.write(card_soup.prettify('utf-8'))

                    # Search for the quality
                    card_condition = card_soup.find(string=re.compile(f'^{self.quality[quality]}'))
                    if card_condition is not None:
                        # Navigate to Price from Quality: Condition -> newline -> price
                        card_price = self.parse_price_from_string(self.get_card_price_element(card_condition))
                        if card_price is not None:
                            card_prices.append(card_price)
            else:
                print(f'Returned status code: {response.status_code}')

            if is_store_buying:
                # Append highest price for card
                if len(card_prices) > 0:
                    self.buying_prices.append(max(card_prices))
                else:
                    self.buying_prices.append('')
            else:
                # Append lowest price for card
                if len(card_prices) > 0:
                    self.selling_prices.append(min(card_prices))
                else:
                    self.selling_prices.append('')

        total_time = time.perf_counter() - begin_time
        print(f"{threading.current_thread().getName()} - total time: {total_time:3.2f} seconds\n")

    def get_card_element(self, element):
        raise NotImplementedError

    def get_card_price_element(self, element):
        raise NotImplementedError

    def parse_price_from_string(self, string):
        try:
            if string is not None:
                return locale.atof(string.split()[1])
        except:
            print(f'Unable to get price from "{string.encode("utf-8")}"')

        return None


class FusionGaming(CardSite):
    def __init__(self, foil):
        super().__init__(foil)

        self.name = 'Fusion'
        self.base_url = 'http://www.fusiongamingonline.com'
        self.url_arg = 'q'
        self.quality = {'NM': 'NM-Mint, English, ', 'LP': 'Light Play, English, ',
                        'MP': 'Moderate Play, English, ', 'HP': 'Heavy Play, English, '}
        self.card_name_element = 'h4'

    def get_card_element(self, element):
        return element.parent.parent.parent.parent

    def get_card_price_element(self, element):
        price_soup = BeautifulSoup(str(element.parent.parent.next_sibling.next_sibling), 'html.parser')
        return price_soup.find('span', class_='regular price', string=True).string


class FaceToFace(CardSite):
    def __init__(self, foil):
        super().__init__(foil)

        self.name = 'FaceToFace'
        self.base_url = 'http://www.facetofacegames.com'
        self.url_arg = 'query'
        self.quality = {'NM': 'Condition: NM-Mint, English', 'LP': 'Condition: Slightly Played, English',
                        'MP': 'Condition: Moderately Played, English', 'HP': 'Condition: Heavily Played, English'}
        self.card_name_element = 'a'

    def get_card_element(self, element):
        return element.parent

    def get_card_price_element(self, element):
        return element.parent.next_sibling.next_sibling.string


class WizardTower(CardSite):
    def __init__(self, foil):
        super().__init__(foil)

        self.name = 'Wizard Tower'
        self.base_url = 'http://www.kanatacg.com'
        self.url_arg = 'query'
        self.quality = {'NM': 'Condition: NM-Mint, English', 'LP': 'Condition: Slightly Played, English',
                        'MP': 'Condition: Moderately Played, English', 'HP': 'Condition: Heavily Played, English'}
        self.card_name_element = 'a'

    def get_card_element(self, element):
        return element.parent

    def get_card_price_element(self, element):
        return element.parent.next_sibling.next_sibling.string


def read_in_card_list(filename):
    card_list = []

    try:
        with open(filename, 'r') as file:
            card_list = file.read()
    except:
        print(f'Failed to read list of cards from "{filename}"')

    return card_list.split('\n')


def export_prices_to_csv(card_list, sites, card_price_list):
    filename = 'prices.csv'
    csv_string = 'Card Name'

    # Get headers for csv
    for site in sites:
        csv_string += f';{site} Selling'
        if len(sites) != len(card_price_list):
            csv_string += f';{site} Buying'
    csv_string += '\n'

    for i, card in enumerate(card_list):
        csv_string += f'{card}'
        for prices in card_price_list:
            # Can't actually use ',' as cards names can have commas
            csv_string += f';{prices[i]}'
        csv_string += '\n'

    try:
        with open(filename, 'w') as file:
            file.write(csv_string)
    except:
        print(f'Failed to write card prices to "{filename}"')

    print(f'Export to "{filename}" complete!')


def parse_args():
    parser = argparse.ArgumentParser()

    # Required Args
    parser.add_argument('card_list_file', help='The file containing the list of cards separated by newlines')

    # Optional Args
    parser.add_argument('-f', '--foil',
                        help='Use this flag if you\'re looking for foils. Default is to not look for foils',
                        action='store_true')
    parser.add_argument('-q', '--quality',
                        help='The quality of card to look for. Valid values are "NM", "LP", "MP", and "HP". Default is "NM"',
                        choices=['NM', 'LP', 'MP', 'HP'], default='NM')
    parser.add_argument('-bl', '--buylist',
                        help='Use this flag if you want to see the buylist prices of the stores, in addition to their sell-list',
                        action='store_true')

    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = parse_args()

        card_list = read_in_card_list(args.card_list_file)
        quality = args.quality
        foil = args.foil
        buy_list = args.buylist

        card_price_list = []
        site_list = []

        # Set locale to current locale
        locale.setlocale(locale.LC_ALL, '')

        is_store_buying = True

        f2f = FaceToFace(foil)
        fusion = FusionGaming(foil)
        wizard_tower = WizardTower(foil)

        site_list.append(f2f.name)
        site_list.append(fusion.name)
        site_list.append(wizard_tower.name)

        thread_list = [
            threading.Thread(target=f2f.get_prices, args=(card_list, quality, not is_store_buying,), name=f2f.name),
            threading.Thread(target=fusion.get_prices, args=(card_list, quality, not is_store_buying,), name=fusion.name),
            threading.Thread(target=wizard_tower.get_prices, args=(card_list, quality, not is_store_buying,), name=wizard_tower.name),
        ]

        for thread in thread_list:
            thread.start()

        for thread in thread_list:
            thread.join()

        if buy_list:
            thread_list = [
                threading.Thread(target=f2f.get_prices, args=(card_list, quality, is_store_buying,), name=f2f.name + ' buylist'),
                threading.Thread(target=fusion.get_prices, args=(card_list, quality, is_store_buying,), name=fusion.name + ' buylist'),
                threading.Thread(target=wizard_tower.get_prices, args=(card_list, quality, is_store_buying,), name=wizard_tower.name + ' buylist'),
            ]

            for thread in thread_list:
                thread.start()

            for thread in thread_list:
                thread.join()

        card_price_list.append(f2f.selling_prices)
        card_price_list.append(fusion.selling_prices)
        card_price_list.append(wizard_tower.selling_prices)
        if buy_list:
            card_price_list.append(f2f.buying_prices)
            card_price_list.append(fusion.buying_prices)
            card_price_list.append(wizard_tower.buying_prices)

        print('Exporting prices to file...')
        export_prices_to_csv(card_list, site_list, card_price_list)
    except KeyboardInterrupt:
        exit(0)
