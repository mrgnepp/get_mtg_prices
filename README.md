# get_mtg_prices
Grabs prices for mtg cards from various sources on the web.

```bash
# Uses Python 3.6
pip install -r requirements.txt
```

Using get_mtg_prices:
```bash
python get_mtg_prices.py -h
```
usage: get_mtg_prices.py [-h] [-q {NM,LP,MP,HP}] [-f] card_list_file

positional arguments:
```
  card_list_file        The file containing the list of cards separated by newlines
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
