# get_mtg_prices
Grabs prices for mtg cards from various sources on the web.

Requires [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup) to be installed.
```bash
# Using pip
pip install beautifulsoup4
```

```bash
python get_mtg_prices.py -h
```
usage: get_mtg_prices.py [-h] [-q {NM,LP,MP,HP}] [-f] card_list_file

positional arguments:
```
  card_list_file        the file containing the list of cards
```
optional arguments:
```
  -h, --help            show this help message and exit
  -q {NM,LP,MP,HP}, --quality {NM,LP,MP,HP}
                        The quality of card to look for. Valid values are
                        "NM", "LP", "MP", and "HP". Default is "NM"
  -f, --foil            Use this flag if you're looking for foils. Default is
                        to not look for foils
```

Example Usage:
```bash
# Defaults to non-foil and Near-Mint quality
python get_mtg_prices.py card_list.txt 
```

```bash
# Foil and Near-Mint quality
python get_mtg_prices.py card_list.txt -f
```

```bash
# Non-foil and Lightly-Played quality
python get_mtg_prices.py card_list.txt -q LP
```
