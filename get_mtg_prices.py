#! /usr/bin/python

import abc
import argparse
import locale
import re

from bs4 import BeautifulSoup
import requests

class CardSite:

    # Abstract class
    abc.__metaclass__ = abc.ABCMeta

    def __init__(self):
        self.selling_prices = []
        self.buying_prices = []

        self.url = ''
        self.sell_list_url = '/products/search?'
        self.buy_list_url = '/buylist/search?'

    def get_prices(self, card_list, is_store_buying, quality):
        if is_store_buying:
            self.url = self.base_url + self.buy_list_url
        else:
            self.url = self.base_url + self.sell_list_url

        for card in card_list:
            card_prices = []
            response = requests.get(self.url, {self.url_arg:card})

            print('Searching... %s' % response.url) 
            if response.status_code == requests.codes.ok:
                soup = BeautifulSoup(response.text, 'html.parser')

                # DEBUG
                # with open('soup.html', 'wb') as file:
                #     file.write(soup.prettify('utf-8'))

                # Ensure we grab the correct card
                elements = soup.find_all(self.card_name_element, string=re.compile('^%s$' % card, re.I))
                for element in elements:
                    # Create new soup to restrict search for card
                    card_soup = BeautifulSoup(str(self.get_card_element(element)), 'html.parser')
                    
                    # DEBUG
                    # with open('card_soup.html', 'wb') as file:
                    #     file.write(card_soup.prettify('utf-8'))

                    # Search for the quality
                    card_condition = card_soup.find(string=re.compile('^%s' % self.quality[quality]))
                    if card_condition is not None:
                        # Navigate to Price from Quality: Condition -> newline -> price
                        card_price = self.parse_price_from_string(self.get_card_price_element(card_condition))
                        if card_price is not None:
                            card_prices.append(card_price)
            else:
                print('Returned status code: %s' % response.status_code)

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

    def get_card_element(self, element):
        raise NotImplementedError

    def get_card_price_element(self, element):
        raise NotImplementedError

    def parse_price_from_string(self, string):
        try:
            if string is not None:
                return locale.atof(string.split()[1])
        except:
            print('Unable to get price from "%s"' % str(string.encode('utf-8')))
        
        return None


class FusionGaming(CardSite):
    def __init__(self):
        super().__init__()

        self.base_url = 'http://www.fusiongamingonline.com'
        self.url_arg = 'q'
        self.quality = {'NM':'NM-Mint, English, ', 'LP':'Light Play, English, ', 'MP':'Moderate Play, English, ', 'HP':'Heavy Play, English, '}
        self.card_name_element = 'h4'

    def get_card_element(self, element):
        return element.parent.parent.parent.parent

    def get_card_price_element(self, element):
        price_soup = BeautifulSoup(str(element.parent.parent.next_sibling.next_sibling), 'html.parser')
        return price_soup.find('span', class_='regular price').string


class FaceToFace(CardSite):
    def __init__(self):
        super().__init__()

        self.base_url = 'http://www.facetofacegames.com'
        self.url_arg = 'query'
        self.quality = {'NM':'Condition: NM-Mint, English', 'LP':'Condition: Slightly Played, English', 'MP':'Condition: Moderately Played, English', 'HP':'Condition: Heavily Played, English'}
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
        print('Failed to read list of cards from "%s"' % filename)

    return card_list.split('\n')

def export_prices_to_csv(card_list, site):
    filename = 'prices.csv'
    csv_string = ''
    
    print('Exporting prices to %s...' % filename)

    for i, card in enumerate(card_list):
        # Can't actually use ',' as cards names can have commas
        csv_string += '%s;%s;%s\n' % (card, str(site.selling_prices[i]), str(site.buying_prices[i]))

    try:
        with open(filename, 'w') as file:
            file.write(csv_string)
    except:
        print('Failed to write card prices to "%s"' % filename)

    print('Export Complete!')

def parse_args():
    parser = argparse.ArgumentParser()

    # Required Args
    parser.add_argument('card_list_file', help='The file containing the list of cards separated by newlines')

    # Optional Args
    parser.add_argument('-q', '--quality', help='The quality of card to look for. Valid values are "NM", "LP", "MP", and "HP". Default is "NM"', choices=['NM', 'LP', 'MP', 'HP'], default='NM')
    parser.add_argument('-f', '--foil', help='Use this flag if you\'re looking for foils. Default is to not look for foils', action='store_true')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    card_list = read_in_card_list(args.card_list_file)
    quality = args.quality
    foil = args.foil

    # Set locale to current locale
    locale.setlocale(locale.LC_ALL, '')
    
    f2f = FaceToFace()
    f2f.get_prices(card_list, False, quality)
    f2f.get_prices(card_list, True, quality)

    export_prices_to_csv(card_list, f2f)

    # fusion = FusionGaming()
    # fusion.get_prices(card_list, False, quality)
    # fusion.get_prices(card_list, True, quality)

    # export_prices_to_csv(card_list, fusion)