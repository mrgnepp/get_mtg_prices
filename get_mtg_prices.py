#! /usr/bin/python

import argparse
import re

from bs4 import BeautifulSoup
import requests

def get_f2f_prices(card_list, quality):
    f2f_url = 'http://www.facetofacegames.com/products/search?'
    f2f_url_arg = 'query'
    f2f_quality = {'NM':'Condition: NM-Mint, English', 'LP':'Condition: Slightly Played, English', 'MP':'Condition: Moderately Played, English', 'HP':'Condition: Heavily Played, English'}
    prices = []

    for card in card_list:
        card_prices = []    
        response = requests.get(f2f_url, {f2f_url_arg:card})

        print('Searching... %s' % response.url) 
        if response.status_code == requests.codes.ok:
            soup = BeautifulSoup(response.text, 'html.parser')

            # DEBUG
            # with open('content.html', 'wb') as file:
            #     file.write(soup.prettify('utf-8'))

            # Search via quality
            elements = soup.find_all('td', {'class':'variantInfo'}, string=f2f_quality[quality])
            for element in elements:
                # Condition -> newline -> price
                card_price = parse_price_from_string(element.next_sibling.next_sibling.string)
                if card_price is not None:
                    card_prices.append(card_price)

        else:
            print('Returned status code: %s' % response.status_code)

        # Append lowest price for card
        if len(card_prices) > 0:
            prices.append(min(card_prices))
        else:
            prices.append('')

    return prices

def get_fusion_prices(card_list):
    fusion_url = 'http://www.fusiongamingonline.com/products/search?'
    fusion_url_arg = 'q'
    fusion_quality = {}
    prices = []

    return None

def parse_price_from_string(string):
    try:
        return float(string.split()[1])
    except:
        print('Unable to get price from "%s"' % string)
        return None

def read_in_card_list(filename):
    card_list = []

    try:
        with open(filename, 'r') as file:
            card_list = file.read()
    except:
        print('Failed to read list of cards from "%s"' % filename)

    return card_list.split('\n')

def export_prices_to_csv(*args):
    filename = 'prices.csv'
    csv_string = ''
    card_list = args[0]
    f2f_prices = args[1]
    
    print('Exporting prices to %s...' % filename)

    for i, card in enumerate(card_list):
        # Can't actually use ',' as cards names can have commas
        csv_string += card + '|' + str(f2f_prices[i]) + '\n'

    try:
        with open(filename, 'w') as file:
            file.write(csv_string)
    except:
        print('Failed to write card prices to "%s"' % filename)

    print('Export Complete!')

def parse_args():
    parser = argparse.ArgumentParser()

    # Required Args
    parser.add_argument('card_list_file', help='the file containing the list of cards')

    # Optional Args
    parser.add_argument('-q', '--quality', help='The quality of card to look for. Valid values are "NM", "LP", "MP", and "HP". Default is "NM"', choices=['NM', 'LP', 'MP', 'HP'], default='NM')
    parser.add_argument('-f', '--foil', help='Use this flag if you\'re looking for foils. Default is to not look for foils', action='store_true')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    
    card_list = read_in_card_list(args.card_list_file)
    quality = args.quality
    foil = args.foil
    
    f2f_prices = get_f2f_prices(card_list, quality)

    export_prices_to_csv(card_list, f2f_prices)