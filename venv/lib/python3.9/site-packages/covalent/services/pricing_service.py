from datetime import datetime
from typing import Generic, TypeVar, List, Optional
import requests
from .util.back_off import ExponentialBackoff
from .util.api_helper import check_and_modify_response, paginate_endpoint, Response
from .util.types import chain, quote, user_agent
from .util.debugger import debug_output


class TokenPricesResponse:
    contract_decimals: int
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    contract_name: str
    """ The string returned by the `name()` method. """
    contract_ticker_symbol: str
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_address: str
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    supports_erc: List[str]
    """ A list of supported standard ERC interfaces, eg: `ERC20` and `ERC721`. """
    logo_url: str
    """ The contract logo URL. """
    update_at: datetime
    quote_currency: str
    """ The requested quote currency eg: `USD`. """
    prices: List["Price"]
    """ List of response items. """
    items: List["Price"]
    """ List of response items. """

    def __init__(self, data):
        self.contract_decimals = int(data["contract_decimals"])
        self.contract_name = data["contract_name"]
        self.contract_ticker_symbol = data["contract_ticker_symbol"]
        self.contract_address = data["contract_address"]
        self.supports_erc = data["supports_erc"]
        self.logo_url = data["logo_url"]
        self.update_at = datetime.fromisoformat(data["update_at"])
        self.quote_currency = data["quote_currency"]
        self.prices = [Price(item_data) for item_data in data["prices"]]
        self.items = [Price(item_data) for item_data in data["items"]]

class Price:
    contract_metadata: Optional["ContractMetadata"]
    date: Optional[datetime]
    """ The date of the price capture. """
    price: Optional[float]
    """ The price in the requested `quote-currency`. """
    pretty_price: Optional[str]
    """ A prettier version of the price for rendering purposes. """

    def __init__(self, data):
        self.date = datetime.fromisoformat(data["date"]) if "date" in data and data["date"] is not None else None
        self.price = data["price"] if "price" in data and data["price"] is not None else None
        self.pretty_price = data["pretty_price"] if "pretty_price" in data and data["pretty_price"] is not None else None
        self.contract_metadata = ContractMetadata(data["contract_metadata"]) if "contract_metadata" in data and data["contract_metadata"] is not None else None

class ContractMetadata:
    contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    supports_erc: Optional[List[str]]
    """ A list of supported standard ERC interfaces, eg: `ERC20` and `ERC721`. """
    logo_url: Optional[str]
    """ The contract logo URL. """

    def __init__(self, data):
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.supports_erc = data["supports_erc"] if "supports_erc" in data and data["supports_erc"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
            


T = TypeVar('T')

class Response(Generic[T]):
    data: Optional[List[T]]
    error: bool
    error_code: Optional[int]
    error_message: Optional[str]

    def __init__(self, data: Optional[List[T]], error: bool, error_code: Optional[int], error_message: Optional[str]):
        self.data = data
        self.error = error
        self.error_code = error_code
        self.error_message = error_message

class PricingService:
    __api_key: str
    __debug: Optional[bool]
    def __init__(self, api_key: str, debug: Optional[bool] = False):
        self.__api_key = api_key
        self.__debug = debug


    def get_token_prices(self, chain_name: chain, quote_currency: quote, contract_address: str, _from: Optional[str] = None, _to: Optional[str] = None, prices_at_asc: Optional[bool] = None) -> Response[TokenPricesResponse]:
        """
        Commonly used to get historic prices of a token between date ranges. Supports native tokens.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        contract_address (str): Contract address for the token. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically. Supports multiple contract addresses separated by commas.
        _from (str): The start day of the historical price range (YYYY-MM-DD).
        _to (str): The end day of the historical price range (YYYY-MM-DD).
        prices_at_asc (bool): Sort the prices in chronological ascending order. By default, it's set to `false` and returns prices in chronological descending order.
        """
        success = False
        data: Optional[Response[TokenPricesResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if _from is not None:
                    url_params["from"] = str(_from)
                    
                if _to is not None:
                    url_params["to"] = str(_to)
                    
                if prices_at_asc is not None:
                    url_params["prices-at-asc"] = str(prices_at_asc)

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/pricing/historical_by_addresses_v2/{chain_name}/{quote_currency}/{contract_address}/", params=url_params, headers={
                    "Authorization": f"Bearer {self.__api_key}",
                    "X-Requested-With": user_agent
                })

                debug_output(response.url, response.status_code, start_time)

                if response.status_code == 429:
                    try:
                        res = backoff.back_off(response.url)
                        data = Response(**res)
                    except Exception as e:
                        success = True
                        return Response(
                            data=None,
                            error=True,
                            error_code=response.status_code,
                            error_message=e
                        )
                else:
                    res = response.json()
                    data = Response(**res)

                res: List[TokenPricesResponse] = []
                for item in data.data:
                    data_class = TokenPricesResponse(item)
                    check_and_modify_response(data_class)
                    res.append(data_class)
                success = True
                return Response(
                    data=res,
                    error=data.error,
                    error_code=data.error_code if data else response.status_code,
                    error_message=data.error_message if data else "Internal server error" if response.status_code == 500 else "401 Authorization Required"
                )
            except Exception:
                success = True
                return Response(
                    data=None,
                    error=True,
                    error_code=data.error_code if data is not None else response.status_code if response is not None else None,
                    error_message=data.error_message if data else "Internal server error" if response.status_code == 500 else "401 Authorization Required"
                )
        return Response(
            data=None,
            error=True,
            error_code=500,
            error_message="Internal server error"
        )
