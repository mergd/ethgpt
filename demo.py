import json

import requests

# Rough ethereum transaction parser which tries to decode events

addresses = ['0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
             '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48']
tokenPrice = {}


restring = """
 {
  "chain": "ethereum",
  "txhash": "0x1e8ea57cb297daffda4db30a3a414395880d912c0dd63dc29f373c0ca3cbbbdd",
  "from": "0x0ab21031124af2165586fbb495d93725a372c227",
  "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": {
    "contract": "0x9008d19f58aabd9ed0d60971565aa8510560ab41",
    "logs": [
      {
        "event": "Interaction",
        "target": "0x40a50cf069e992aa4536211b23f286ef88752187",
        "value": "0",
        "selector": ""
      },
      {
        "event": "Trade",
        "owner": "0x40a50cf069e992aa4536211b23f286ef88752187",
        "sellToken": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
        "buyToken": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "sellAmount": "5.645",
        "buyAmount": "118540273181",
        "feeAmount": "12983804406807450",
        "orderUid": "0000000000000000000000000000000000000000000000000000000000000038cec22aa9cc949e98e28a35842da978eb085711988f0bb6fcb7fcfa82c62b4b4340a50cf069e992aa4536211b23f286ef88752187ffffffff0000000000000000"
      },
      {
        "event": "Interaction",
        "target": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
        "value": "0",
        "selector": ""
      },
      {
        "event": "Interaction",
        "target": "0xaf9b571e36543be67fbcc979f6d52a2dbb2e2c56",
        "value": "0",
        "selector": ""
      },
      {
        "event": "Settlement",
        "solver": "0x0ab21031124af2165586fbb495d93725a372c227"
      }
    ],
    "call": {
      "contract": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
      "logs": [],
      "call": {
        "contract": "0xa2327a938febf5fec13bacfb16ae10ecbc4cbdcf",
        "logs": [
          {
            "event": "Transfer",
            "from": "0x9008d19f58aabd9ed0d60971565aa8510560ab41",
            "to": "0xca0312915cd1f76f3829f2e08a17e9e07bc21cb0",
            "value": "118540273181"
          }
        ]
      }
    }
  }
}
"""


def pullTokenInfo():
    # query llamafi for price and name
    url = 'https://coins.llama.fi/prices/current/'
    for address in addresses:
        url += (f"ethereum:{address},")
    print(url)
    response = requests.get(url)
    response.raise_for_status()

    res = response.json()['coins']
    keys = res.keys()

    for coin in keys:
        # substring the ethereum:
        print(coin[9:])
        coin_name = coin[9:].lower()
        coin_info = res[coin]
        coin_price = coin_info['price']
        symbol = coin_info['symbol']
        fstring = f"{symbol}  (${coin_price})"
        tokenPrice[coin_name] = (fstring)

    print(tokenPrice)
    # print(response.json())


def replace_keys(d):
    for key in list(d.keys()):
        if isinstance(d[key], dict):
            d[key] = replace_keys(d[key])  # Recurse into nested dictionaries
        lower_key = key.lower()
        for token_key in tokenPrice:
            if lower_key == token_key.lower():
                d[tokenPrice[token_key]] = d.pop(key)
                break
    return d


def processStr():
    pullTokenInfo()
    modified_restring = restring
    for token_key in tokenPrice:
        modified_restring = modified_restring.replace(
            token_key, tokenPrice[token_key])
    jsonstr = json.loads(modified_restring)
    print(jsonstr)


processStr()
