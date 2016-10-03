# Morgan Epp

import urllib.request
import urllib.parse
import re

from bs4 import BeautifulSoup

def get_f2f_prices(card_list, quality):
    f2f_url = 'http://www.facetofacegames.com/products/search?'
    f2f_url_arg = 'query'
    f2f_quality = {'NM':'Condition: NM-Mint, English', 'LP':'Condition: Slightly Played, English', 'MP':'Condition: Moderately Played, English', 'HP':'Condition: Heavily Played, English'}
    prices = []

    for card in card_list:
        card_prices = []
        card_url = f2f_url + urllib.parse.urlencode({f2f_url_arg:card}) # Replaces spaces, commas, etc. in card name
        print("Searching... " + card_url) 

        with urllib.request.urlopen(card_url) as response:
            content = response.read()
            soup = BeautifulSoup(content, 'html.parser')

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

        # Append lowest price for card
        if len(card_prices) > 0:
            prices.append(min(card_prices))
        else:
            prices.append("")

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

def export_prices_to_csv(*args):
    filename = 'prices.csv'
    csv_string = ''
    card_list = args[0]
    f2f_prices = args[1]
    
    print('Exporting prices to %s...' % filename)

    for i, card in enumerate(card_list):
        csv_string += card + ',' + str(f2f_prices[0]) + '\n'

    with open(filename, 'w') as file:
        file.write(csv_string)

    print('Export Complete!')

if __name__ == '__main__':
    card_list = ['Counterspell', 'Kalemne, Disciple of Iroas']
    quality = ['NM', 'LP', 'MP', 'HP']
    foil = False
    
    f2f_prices = get_f2f_prices(card_list, quality[0])
    #print(f2f_prices)
    export_prices_to_csv(card_list, f2f_prices)