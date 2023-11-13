from datetime import datetime
from typing import Generic, TypeVar, List, Optional
import requests
from .util.back_off import ExponentialBackoff
from .util.api_helper import check_and_modify_response, paginate_endpoint, Response
from .util.types import chain, quote, user_agent
from .util.debugger import debug_output

class PoolResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["Pool"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [Pool(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class Pool:
    exchange: Optional[str]
    """ The pair address. """
    swap_count_24h: Optional[str]
    total_liquidity_quote: Optional[str]
    """ The total liquidity converted to fiat in `quote-currency`. """
    volume_24h_quote: Optional[str]
    fee_24h_quote: Optional[str]
    total_supply: Optional[int]
    """ Total supply of this pool token. """
    quote_rate: Optional[str]
    """ The exchange rate for the requested quote currency. """
    chain_name: Optional[str]
    """ The requested chain name eg: `eth-mainnet`. """
    chain_id: Optional[str]
    """ The requested chain ID eg: `1`. """
    dex_name: Optional[str]
    """ The name of the DEX, eg: `uniswap_v2`. """
    volume_7d_quote: Optional[str]
    annualized_fee: Optional[str]
    token_0: Optional["Token"]
    token_1: Optional["Token"]

    def __init__(self, data):
        self.exchange = data["exchange"] if "exchange" in data and data["exchange"] is not None else None
        self.swap_count_24h = data["swap_count_24h"] if "swap_count_24h" in data and data["swap_count_24h"] is not None else None
        self.total_liquidity_quote = data["total_liquidity_quote"] if "total_liquidity_quote" in data and data["total_liquidity_quote"] is not None else None
        self.volume_24h_quote = data["volume_24h_quote"] if "volume_24h_quote" in data and data["volume_24h_quote"] is not None else None
        self.fee_24h_quote = data["fee_24h_quote"] if "fee_24h_quote" in data and data["fee_24h_quote"] is not None else None
        self.total_supply = int(data["total_supply"]) if "total_supply" in data and data["total_supply"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
        self.chain_name = data["chain_name"] if "chain_name" in data and data["chain_name"] is not None else None
        self.chain_id = data["chain_id"] if "chain_id" in data and data["chain_id"] is not None else None
        self.dex_name = data["dex_name"] if "dex_name" in data and data["dex_name"] is not None else None
        self.volume_7d_quote = data["volume_7d_quote"] if "volume_7d_quote" in data and data["volume_7d_quote"] is not None else None
        self.annualized_fee = data["annualized_fee"] if "annualized_fee" in data and data["annualized_fee"] is not None else None
        self.token_0 = Token(data["token_0"]) if "token_0" in data and data["token_0"] is not None else None
        self.token_1 = Token(data["token_1"]) if "token_1" in data and data["token_1"] is not None else None

class Pagination:
    has_more: Optional[bool]
    """ True is there is another page. """
    page_number: Optional[int]
    """ The requested page number. """
    page_size: Optional[int]
    """ The requested number of items on the current page. """
    total_count: Optional[int]
    """ The total number of items across all pages for this request. """

    def __init__(self, data):
        self.has_more = data["has_more"] if "has_more" in data and data["has_more"] is not None else None
        self.page_number = int(data["page_number"]) if "page_number" in data and data["page_number"] is not None else None
        self.page_size = int(data["page_size"]) if "page_size" in data and data["page_size"] is not None else None
        self.total_count = int(data["total_count"]) if "total_count" in data and data["total_count"] is not None else None
            

class Token:
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    volume_in_24h: Optional[str]
    volume_out_24h: Optional[str]
    quote_rate: Optional[str]
    """ The exchange rate for the requested quote currency. """
    reserve: Optional[str]
    logo_url: Optional[str]
    """ The contract logo URL. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_decimals: Optional[str]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    volume_in_7d: Optional[str]
    volume_out_7d: Optional[str]

    def __init__(self, data):
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.volume_in_24h = data["volume_in_24h"] if "volume_in_24h" in data and data["volume_in_24h"] is not None else None
        self.volume_out_24h = data["volume_out_24h"] if "volume_out_24h" in data and data["volume_out_24h"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
        self.reserve = data["reserve"] if "reserve" in data and data["reserve"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_decimals = data["contract_decimals"] if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.volume_in_7d = data["volume_in_7d"] if "volume_in_7d" in data and data["volume_in_7d"] is not None else None
        self.volume_out_7d = data["volume_out_7d"] if "volume_out_7d" in data and data["volume_out_7d"] is not None else None
            

class PoolToDexResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    address: str
    """ The requested address. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["PoolToDexItem"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.address = data["address"]
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [PoolToDexItem(item_data) for item_data in data["items"]]

class SupportedDex:
    chain_id: Optional[str]
    """ The requested chain ID eg: `1`. """
    chain_name: Optional[str]
    """ The requested chain name eg: `eth-mainnet`. """
    dex_name: Optional[str]
    """ The name of the DEX, eg: `uniswap_v2`. """
    factory_contract_address: Optional[str]
    router_contract_addresses: Optional[List[str]]
    swap_fee: Optional[float]

    def __init__(self, data):
        self.chain_id = data["chain_id"] if "chain_id" in data and data["chain_id"] is not None else None
        self.chain_name = data["chain_name"] if "chain_name" in data and data["chain_name"] is not None else None
        self.dex_name = data["dex_name"] if "dex_name" in data and data["dex_name"] is not None else None
        self.factory_contract_address = data["factory_contract_address"] if "factory_contract_address" in data and data["factory_contract_address"] is not None else None
        self.router_contract_addresses = data["router_contract_addresses"] if "router_contract_addresses" in data and data["router_contract_addresses"] is not None else None
        self.swap_fee = data["swap_fee"] if "swap_fee" in data and data["swap_fee"] is not None else None

class PoolToDexItem(SupportedDex):
    logo_url: Optional[str]
    """ The dex logo URL. """
    def __init__(self, data):
        super().__init__(data)
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None

class PoolByAddressResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["PoolWithTimeseries"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [PoolWithTimeseries(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class PoolWithTimeseries:
    exchange: Optional[str]
    """ The pair address. """
    swap_count_24h: Optional[str]
    total_liquidity_quote: Optional[str]
    """ The total liquidity converted to fiat in `quote-currency`. """
    volume_24h_quote: Optional[str]
    fee_24h_quote: Optional[str]
    total_supply: Optional[int]
    """ Total supply of this pool token. """
    quote_rate: Optional[str]
    """ The exchange rate for the requested quote currency. """
    chain_id: Optional[str]
    """ The requested chain ID eg: `1`. """
    dex_name: Optional[str]
    """ The name of the DEX, eg: `uniswap_v2`. """
    volume_7d_quote: Optional[str]
    annualized_fee: Optional[str]
    token_0: Optional["Token"]
    token_1: Optional["Token"]
    token_0_reserve_quote: Optional[str]
    token_1_reserve_quote: Optional[str]
    volume_timeseries_7d: Optional[List["VolumeTimeseries"]]
    volume_timeseries_30d: Optional[List["VolumeTimeseries"]]
    liquidity_timeseries_7d: Optional[List["LiquidityTimeseries"]]
    liquidity_timeseries_30d: Optional[List["LiquidityTimeseries"]]
    price_timeseries_7d: Optional[List["PriceTimeseries"]]
    price_timeseries_30d: Optional[List["PriceTimeseries"]]

    def __init__(self, data):
        self.exchange = data["exchange"] if "exchange" in data and data["exchange"] is not None else None
        self.swap_count_24h = data["swap_count_24h"] if "swap_count_24h" in data and data["swap_count_24h"] is not None else None
        self.total_liquidity_quote = data["total_liquidity_quote"] if "total_liquidity_quote" in data and data["total_liquidity_quote"] is not None else None
        self.volume_24h_quote = data["volume_24h_quote"] if "volume_24h_quote" in data and data["volume_24h_quote"] is not None else None
        self.fee_24h_quote = data["fee_24h_quote"] if "fee_24h_quote" in data and data["fee_24h_quote"] is not None else None
        self.total_supply = int(data["total_supply"]) if "total_supply" in data and data["total_supply"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
        self.chain_id = data["chain_id"] if "chain_id" in data and data["chain_id"] is not None else None
        self.dex_name = data["dex_name"] if "dex_name" in data and data["dex_name"] is not None else None
        self.volume_7d_quote = data["volume_7d_quote"] if "volume_7d_quote" in data and data["volume_7d_quote"] is not None else None
        self.annualized_fee = data["annualized_fee"] if "annualized_fee" in data and data["annualized_fee"] is not None else None
        self.token_0_reserve_quote = data["token_0_reserve_quote"] if "token_0_reserve_quote" in data and data["token_0_reserve_quote"] is not None else None
        self.token_1_reserve_quote = data["token_1_reserve_quote"] if "token_1_reserve_quote" in data and data["token_1_reserve_quote"] is not None else None
        self.token_0 = Token(data["token_0"]) if "token_0" in data and data["token_0"] is not None else None
        self.token_1 = Token(data["token_1"]) if "token_1" in data and data["token_1"] is not None else None
        self.volume_timeseries_7d = [VolumeTimeseries(item_data) for item_data in data["volume_timeseries_7d"]] if "volume_timeseries_7d" in data and data["volume_timeseries_7d"] is not None else None
        self.volume_timeseries_30d = [VolumeTimeseries(item_data) for item_data in data["volume_timeseries_30d"]] if "volume_timeseries_30d" in data and data["volume_timeseries_30d"] is not None else None
        self.liquidity_timeseries_7d = [LiquidityTimeseries(item_data) for item_data in data["liquidity_timeseries_7d"]] if "liquidity_timeseries_7d" in data and data["liquidity_timeseries_7d"] is not None else None
        self.liquidity_timeseries_30d = [LiquidityTimeseries(item_data) for item_data in data["liquidity_timeseries_30d"]] if "liquidity_timeseries_30d" in data and data["liquidity_timeseries_30d"] is not None else None
        self.price_timeseries_7d = [PriceTimeseries(item_data) for item_data in data["price_timeseries_7d"]] if "price_timeseries_7d" in data and data["price_timeseries_7d"] is not None else None
        self.price_timeseries_30d = [PriceTimeseries(item_data) for item_data in data["price_timeseries_30d"]] if "price_timeseries_30d" in data and data["price_timeseries_30d"] is not None else None

class VolumeTimeseries:
    dex_name: Optional[str]
    """ The name of the DEX, eg: `uniswap_v2`. """
    chain_id: Optional[str]
    """ The requested chain ID eg: `1`. """
    dt: Optional[str]
    exchange: Optional[str]
    """ The pair address. """
    sum_amount_0_in: Optional[str]
    sum_amount_0_out: Optional[str]
    sum_amount_1_in: Optional[str]
    sum_amount_1_out: Optional[str]
    volume_quote: Optional[str]
    token_0_quote_rate: Optional[str]
    token_1_quote_rate: Optional[str]
    swap_count_24: Optional[str]

    def __init__(self, data):
        self.dex_name = data["dex_name"] if "dex_name" in data and data["dex_name"] is not None else None
        self.chain_id = data["chain_id"] if "chain_id" in data and data["chain_id"] is not None else None
        self.dt = data["dt"] if "dt" in data and data["dt"] is not None else None
        self.exchange = data["exchange"] if "exchange" in data and data["exchange"] is not None else None
        self.sum_amount_0_in = data["sum_amount_0_in"] if "sum_amount_0_in" in data and data["sum_amount_0_in"] is not None else None
        self.sum_amount_0_out = data["sum_amount_0_out"] if "sum_amount_0_out" in data and data["sum_amount_0_out"] is not None else None
        self.sum_amount_1_in = data["sum_amount_1_in"] if "sum_amount_1_in" in data and data["sum_amount_1_in"] is not None else None
        self.sum_amount_1_out = data["sum_amount_1_out"] if "sum_amount_1_out" in data and data["sum_amount_1_out"] is not None else None
        self.volume_quote = data["volume_quote"] if "volume_quote" in data and data["volume_quote"] is not None else None
        self.token_0_quote_rate = data["token_0_quote_rate"] if "token_0_quote_rate" in data and data["token_0_quote_rate"] is not None else None
        self.token_1_quote_rate = data["token_1_quote_rate"] if "token_1_quote_rate" in data and data["token_1_quote_rate"] is not None else None
        self.swap_count_24 = data["swap_count_24"] if "swap_count_24" in data and data["swap_count_24"] is not None else None
            

class LiquidityTimeseries:
    dex_name: Optional[str]
    """ The name of the DEX, eg: `uniswap_v2`. """
    chain_id: Optional[str]
    """ The requested chain ID eg: `1`. """
    dt: Optional[str]
    exchange: Optional[str]
    """ The pair address. """
    r0_c: Optional[str]
    r1_c: Optional[str]
    liquidity_quote: Optional[str]
    token_0_quote_rate: Optional[str]
    token_1_quote_rate: Optional[str]

    def __init__(self, data):
        self.dex_name = data["dex_name"] if "dex_name" in data and data["dex_name"] is not None else None
        self.chain_id = data["chain_id"] if "chain_id" in data and data["chain_id"] is not None else None
        self.dt = data["dt"] if "dt" in data and data["dt"] is not None else None
        self.exchange = data["exchange"] if "exchange" in data and data["exchange"] is not None else None
        self.r0_c = data["r0_c"] if "r0_c" in data and data["r0_c"] is not None else None
        self.r1_c = data["r1_c"] if "r1_c" in data and data["r1_c"] is not None else None
        self.liquidity_quote = data["liquidity_quote"] if "liquidity_quote" in data and data["liquidity_quote"] is not None else None
        self.token_0_quote_rate = data["token_0_quote_rate"] if "token_0_quote_rate" in data and data["token_0_quote_rate"] is not None else None
        self.token_1_quote_rate = data["token_1_quote_rate"] if "token_1_quote_rate" in data and data["token_1_quote_rate"] is not None else None
            

class PriceTimeseries:
    dex_name: Optional[str]
    """ The name of the DEX, eg: `uniswap_v2`. """
    chain_id: Optional[str]
    """ The requested chain ID eg: `1`. """
    dt: Optional[str]
    exchange: Optional[str]
    """ The pair address. """
    price_of_token_0_in_token_1: Optional[str]
    price_of_token_0_in_token_1_description: Optional[str]
    price_of_token_1_in_token_0: Optional[str]
    price_of_token_1_in_token_0_description: Optional[str]
    quote_currency: Optional[str]
    """ The requested quote currency eg: `USD`. """
    price_of_token_0_in_quote_currency: Optional[str]
    price_of_token_1_in_quote_currency: Optional[str]

    def __init__(self, data):
        self.dex_name = data["dex_name"] if "dex_name" in data and data["dex_name"] is not None else None
        self.chain_id = data["chain_id"] if "chain_id" in data and data["chain_id"] is not None else None
        self.dt = data["dt"] if "dt" in data and data["dt"] is not None else None
        self.exchange = data["exchange"] if "exchange" in data and data["exchange"] is not None else None
        self.price_of_token_0_in_token_1 = data["price_of_token_0_in_token_1"] if "price_of_token_0_in_token_1" in data and data["price_of_token_0_in_token_1"] is not None else None
        self.price_of_token_0_in_token_1_description = data["price_of_token_0_in_token_1_description"] if "price_of_token_0_in_token_1_description" in data and data["price_of_token_0_in_token_1_description"] is not None else None
        self.price_of_token_1_in_token_0 = data["price_of_token_1_in_token_0"] if "price_of_token_1_in_token_0" in data and data["price_of_token_1_in_token_0"] is not None else None
        self.price_of_token_1_in_token_0_description = data["price_of_token_1_in_token_0_description"] if "price_of_token_1_in_token_0_description" in data and data["price_of_token_1_in_token_0_description"] is not None else None
        self.quote_currency = data["quote_currency"] if "quote_currency" in data and data["quote_currency"] is not None else None
        self.price_of_token_0_in_quote_currency = data["price_of_token_0_in_quote_currency"] if "price_of_token_0_in_quote_currency" in data and data["price_of_token_0_in_quote_currency"] is not None else None
        self.price_of_token_1_in_quote_currency = data["price_of_token_1_in_quote_currency"] if "price_of_token_1_in_quote_currency" in data and data["price_of_token_1_in_quote_currency"] is not None else None
            

class PoolsDexDataResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    address: str
    """ The requested address. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    quote_currency: str
    """ The requested quote currency eg: `USD`. """
    items: List["PoolsDexDataItem"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.address = data["address"]
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.quote_currency = data["quote_currency"]
        self.items = [PoolsDexDataItem(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class PoolsDexDataItem:
    dex_name: Optional[str]
    """ The name of the DEX, eg: `uniswap_v2`. """
    exchange: Optional[str]
    """ The pair address. """
    exchange_ticker_symbol: Optional[str]
    """ The combined ticker symbol of token0 and token1 separated with a hypen. """
    exchange_logo_url: Optional[str]
    """ The dex logo URL for the pair address. """
    total_liquidity_quote: Optional[float]
    """ The total liquidity converted to fiat in `quote-currency`. """
    pretty_total_liquidity_quote: Optional[str]
    """ A prettier version of the total liquidity quote for rendering purposes. """
    volume_24h_quote: Optional[float]
    """ The volume 24h converted to fiat in `quote-currency`. """
    volume_7d_quote: Optional[float]
    """ The volume 7d converted to fiat in `quote-currency`. """
    fee_24h_quote: Optional[float]
    """ The fee 24h converted to fiat in `quote-currency`. """
    pretty_volume_24h_quote: Optional[str]
    """ A prettier version of the volume 24h quote for rendering purposes. """
    pretty_volume_7d_quote: Optional[str]
    """ A prettier version of the volume 7d quote for rendering purposes. """
    pretty_fee_24h_quote: Optional[str]
    """ A prettier version of the fee 24h quote for rendering purposes. """
    token_0: Optional["PoolsDexToken"]
    """ Token0's contract metadata and reserve data. """
    token_1: Optional["PoolsDexToken"]
    """ Token1's contract metadata and reserve data. """

    def __init__(self, data):
        self.dex_name = data["dex_name"] if "dex_name" in data and data["dex_name"] is not None else None
        self.exchange = data["exchange"] if "exchange" in data and data["exchange"] is not None else None
        self.exchange_ticker_symbol = data["exchange_ticker_symbol"] if "exchange_ticker_symbol" in data and data["exchange_ticker_symbol"] is not None else None
        self.exchange_logo_url = data["exchange_logo_url"] if "exchange_logo_url" in data and data["exchange_logo_url"] is not None else None
        self.total_liquidity_quote = data["total_liquidity_quote"] if "total_liquidity_quote" in data and data["total_liquidity_quote"] is not None else None
        self.pretty_total_liquidity_quote = data["pretty_total_liquidity_quote"] if "pretty_total_liquidity_quote" in data and data["pretty_total_liquidity_quote"] is not None else None
        self.volume_24h_quote = data["volume_24h_quote"] if "volume_24h_quote" in data and data["volume_24h_quote"] is not None else None
        self.volume_7d_quote = data["volume_7d_quote"] if "volume_7d_quote" in data and data["volume_7d_quote"] is not None else None
        self.fee_24h_quote = data["fee_24h_quote"] if "fee_24h_quote" in data and data["fee_24h_quote"] is not None else None
        self.pretty_volume_24h_quote = data["pretty_volume_24h_quote"] if "pretty_volume_24h_quote" in data and data["pretty_volume_24h_quote"] is not None else None
        self.pretty_volume_7d_quote = data["pretty_volume_7d_quote"] if "pretty_volume_7d_quote" in data and data["pretty_volume_7d_quote"] is not None else None
        self.pretty_fee_24h_quote = data["pretty_fee_24h_quote"] if "pretty_fee_24h_quote" in data and data["pretty_fee_24h_quote"] is not None else None
        self.token_0 = PoolsDexToken(data["token_0"]) if "token_0" in data and data["token_0"] is not None else None
        self.token_1 = PoolsDexToken(data["token_1"]) if "token_1" in data and data["token_1"] is not None else None

class PoolsDexToken:
    reserve: Optional[str]
    """ The reserves for the token. """
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    logo_url: Optional[str]
    """ The contract logo URL. """
    quote_rate: Optional[float]
    """ The exchange rate for the requested quote currency. """

    def __init__(self, data):
        self.reserve = data["reserve"] if "reserve" in data and data["reserve"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
            

class AddressExchangeBalancesResponse:
    address: str
    """ The requested address. """
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["UniswapLikeBalanceItem"]
    """ List of response items. """

    def __init__(self, data):
        self.address = data["address"]
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [UniswapLikeBalanceItem(item_data) for item_data in data["items"]]

class UniswapLikeBalanceItem:
    token_0: Optional["UniswapLikeToken"]
    token_1: Optional["UniswapLikeToken"]
    pool_token: Optional["UniswapLikeTokenWithSupply"]

    def __init__(self, data):
        
        self.token_0 = UniswapLikeToken(data["token_0"]) if "token_0" in data and data["token_0"] is not None else None
        self.token_1 = UniswapLikeToken(data["token_1"]) if "token_1" in data and data["token_1"] is not None else None
        self.pool_token = UniswapLikeTokenWithSupply(data["pool_token"]) if "pool_token" in data and data["pool_token"] is not None else None

class UniswapLikeToken:
    contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    logo_url: Optional[str]
    """ The contract logo URL. """
    balance: Optional[int]
    """ The asset balance. Use `contract_decimals` to scale this balance for display purposes. """
    quote: Optional[float]
    quote_rate: Optional[float]
    """ The exchange rate for the requested quote currency. """

    def __init__(self, data):
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.balance = int(data["balance"]) if "balance" in data and data["balance"] is not None else None
        self.quote = data["quote"] if "quote" in data and data["quote"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
            

class UniswapLikeTokenWithSupply:
    contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    logo_url: Optional[str]
    """ The contract logo URL. """
    balance: Optional[int]
    """ The asset balance. Use `contract_decimals` to scale this balance for display purposes. """
    quote: Optional[float]
    quote_rate: Optional[float]
    """ The exchange rate for the requested quote currency. """
    total_supply: Optional[int]
    """ Total supply of this pool token. """

    def __init__(self, data):
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.balance = int(data["balance"]) if "balance" in data and data["balance"] is not None else None
        self.quote = data["quote"] if "quote" in data and data["quote"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
        self.total_supply = int(data["total_supply"]) if "total_supply" in data and data["total_supply"] is not None else None
            

class NetworkExchangeTokensResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["TokenV2Volume"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [TokenV2Volume(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class TokenV2Volume:
    chain_name: Optional[str]
    """ The requested chain name eg: `eth-mainnet`. """
    chain_id: Optional[str]
    """ The requested chain ID eg: `1`. """
    dex_name: Optional[str]
    """ The name of the DEX, eg: `uniswap_v2`. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    total_liquidity: Optional[int]
    total_volume24h: Optional[int]
    logo_url: Optional[str]
    """ The contract logo URL. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    swap_count_24h: Optional[int]
    quote_rate: Optional[float]
    """ The exchange rate for the requested quote currency. """
    total_liquidity_quote: Optional[float]
    """ The total liquidity converted to fiat in `quote-currency`. """
    total_volume_24h_quote: Optional[float]

    def __init__(self, data):
        self.chain_name = data["chain_name"] if "chain_name" in data and data["chain_name"] is not None else None
        self.chain_id = data["chain_id"] if "chain_id" in data and data["chain_id"] is not None else None
        self.dex_name = data["dex_name"] if "dex_name" in data and data["dex_name"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.total_liquidity = int(data["total_liquidity"]) if "total_liquidity" in data and data["total_liquidity"] is not None else None
        self.total_volume24h = int(data["total_volume24h"]) if "total_volume24h" in data and data["total_volume24h"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.swap_count_24h = int(data["swap_count_24h"]) if "swap_count_24h" in data and data["swap_count_24h"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
        self.total_liquidity_quote = data["total_liquidity_quote"] if "total_liquidity_quote" in data and data["total_liquidity_quote"] is not None else None
        self.total_volume_24h_quote = data["total_volume_24h_quote"] if "total_volume_24h_quote" in data and data["total_volume_24h_quote"] is not None else None
            

class SupportedDexesResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    items: List["SupportedDex"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.items = [SupportedDex(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class SingleNetworkExchangeTokenResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["PoolWithTimeseries"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [PoolWithTimeseries(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class TransactionsForAccountAddressResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["ExchangeTransaction"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [ExchangeTransaction(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class ExchangeTransaction:
    block_signed_at: Optional[datetime]
    """ The block signed timestamp in UTC. """
    tx_hash: Optional[str]
    """ The requested transaction hash. """
    act: Optional[str]
    address: Optional[str]
    """ The requested address. """
    amount0: Optional[int]
    amount1: Optional[int]
    amount0_in: Optional[int]
    amount0_out: Optional[int]
    amount1_out: Optional[int]
    to_address: Optional[str]
    from_address: Optional[str]
    sender_address: Optional[str]
    total_quote: Optional[float]
    token_0: Optional["PoolToken"]
    token_1: Optional["PoolToken"]
    token_0_quote_rate: Optional[float]
    token_1_quote_rate: Optional[float]

    def __init__(self, data):
        self.block_signed_at = datetime.fromisoformat(data["block_signed_at"]) if "block_signed_at" in data and data["block_signed_at"] is not None else None
        self.tx_hash = data["tx_hash"] if "tx_hash" in data and data["tx_hash"] is not None else None
        self.act = data["act"] if "act" in data and data["act"] is not None else None
        self.address = data["address"] if "address" in data and data["address"] is not None else None
        self.amount0 = int(data["amount0"]) if "amount0" in data and data["amount0"] is not None else None
        self.amount1 = int(data["amount1"]) if "amount1" in data and data["amount1"] is not None else None
        self.amount0_in = int(data["amount0_in"]) if "amount0_in" in data and data["amount0_in"] is not None else None
        self.amount0_out = int(data["amount0_out"]) if "amount0_out" in data and data["amount0_out"] is not None else None
        self.amount1_out = int(data["amount1_out"]) if "amount1_out" in data and data["amount1_out"] is not None else None
        self.to_address = data["to_address"] if "to_address" in data and data["to_address"] is not None else None
        self.from_address = data["from_address"] if "from_address" in data and data["from_address"] is not None else None
        self.sender_address = data["sender_address"] if "sender_address" in data and data["sender_address"] is not None else None
        self.total_quote = data["total_quote"] if "total_quote" in data and data["total_quote"] is not None else None
        self.token_0_quote_rate = data["token_0_quote_rate"] if "token_0_quote_rate" in data and data["token_0_quote_rate"] is not None else None
        self.token_1_quote_rate = data["token_1_quote_rate"] if "token_1_quote_rate" in data and data["token_1_quote_rate"] is not None else None
        self.token_0 = PoolToken(data["token_0"]) if "token_0" in data and data["token_0"] is not None else None
        self.token_1 = PoolToken(data["token_1"]) if "token_1" in data and data["token_1"] is not None else None

class PoolToken:
    contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    supports_erc: Optional[bool]
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
            

class TransactionsForTokenAddressResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["ExchangeTransaction"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [ExchangeTransaction(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class TransactionsForExchangeResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["ExchangeTransaction"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [ExchangeTransaction(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class EcosystemChartDataResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["UniswapLikeEcosystemCharts"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [UniswapLikeEcosystemCharts(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class UniswapLikeEcosystemCharts:
    dex_name: Optional[str]
    """ The name of the DEX, eg: `uniswap_v2`. """
    chain_id: Optional[str]
    """ The requested chain ID eg: `1`. """
    quote_currency: Optional[str]
    """ The requested quote currency eg: `USD`. """
    gas_token_price_quote: Optional[float]
    total_swaps24h: Optional[int]
    total_active_pairs7d: Optional[int]
    total_fees24h: Optional[float]
    volume_chart7d: Optional[List["VolumeEcosystemChart"]]
    volume_chart30d: Optional[List["VolumeEcosystemChart"]]
    liquidity_chart7d: Optional[List["LiquidityEcosystemChart"]]
    liquidity_chart30d: Optional[List["LiquidityEcosystemChart"]]

    def __init__(self, data):
        self.dex_name = data["dex_name"] if "dex_name" in data and data["dex_name"] is not None else None
        self.chain_id = data["chain_id"] if "chain_id" in data and data["chain_id"] is not None else None
        self.quote_currency = data["quote_currency"] if "quote_currency" in data and data["quote_currency"] is not None else None
        self.gas_token_price_quote = data["gas_token_price_quote"] if "gas_token_price_quote" in data and data["gas_token_price_quote"] is not None else None
        self.total_swaps24h = int(data["total_swaps24h"]) if "total_swaps24h" in data and data["total_swaps24h"] is not None else None
        self.total_active_pairs7d = int(data["total_active_pairs7d"]) if "total_active_pairs7d" in data and data["total_active_pairs7d"] is not None else None
        self.total_fees24h = data["total_fees24h"] if "total_fees24h" in data and data["total_fees24h"] is not None else None
        self.volume_chart7d = [VolumeEcosystemChart(item_data) for item_data in data["volume_chart7d"]] if "volume_chart7d" in data and data["volume_chart7d"] is not None else None
        self.volume_chart30d = [VolumeEcosystemChart(item_data) for item_data in data["volume_chart30d"]] if "volume_chart30d" in data and data["volume_chart30d"] is not None else None
        self.liquidity_chart7d = [LiquidityEcosystemChart(item_data) for item_data in data["liquidity_chart7d"]] if "liquidity_chart7d" in data and data["liquidity_chart7d"] is not None else None
        self.liquidity_chart30d = [LiquidityEcosystemChart(item_data) for item_data in data["liquidity_chart30d"]] if "liquidity_chart30d" in data and data["liquidity_chart30d"] is not None else None

class VolumeEcosystemChart:
    dex_name: Optional[str]
    """ The name of the DEX, eg: `uniswap_v2`. """
    chain_id: Optional[str]
    """ The requested chain ID eg: `1`. """
    dt: Optional[datetime]
    quote_currency: Optional[str]
    """ The requested quote currency eg: `USD`. """
    volume_quote: Optional[float]
    swap_count_24: Optional[int]

    def __init__(self, data):
        self.dex_name = data["dex_name"] if "dex_name" in data and data["dex_name"] is not None else None
        self.chain_id = data["chain_id"] if "chain_id" in data and data["chain_id"] is not None else None
        self.dt = datetime.fromisoformat(data["dt"]) if "dt" in data and data["dt"] is not None else None
        self.quote_currency = data["quote_currency"] if "quote_currency" in data and data["quote_currency"] is not None else None
        self.volume_quote = data["volume_quote"] if "volume_quote" in data and data["volume_quote"] is not None else None
        self.swap_count_24 = int(data["swap_count_24"]) if "swap_count_24" in data and data["swap_count_24"] is not None else None
            

class LiquidityEcosystemChart:
    dex_name: Optional[str]
    """ The name of the DEX, eg: `uniswap_v2`. """
    chain_id: Optional[str]
    """ The requested chain ID eg: `1`. """
    dt: Optional[datetime]
    quote_currency: Optional[str]
    """ The requested quote currency eg: `USD`. """
    liquidity_quote: Optional[float]

    def __init__(self, data):
        self.dex_name = data["dex_name"] if "dex_name" in data and data["dex_name"] is not None else None
        self.chain_id = data["chain_id"] if "chain_id" in data and data["chain_id"] is not None else None
        self.dt = datetime.fromisoformat(data["dt"]) if "dt" in data and data["dt"] is not None else None
        self.quote_currency = data["quote_currency"] if "quote_currency" in data and data["quote_currency"] is not None else None
        self.liquidity_quote = data["liquidity_quote"] if "liquidity_quote" in data and data["liquidity_quote"] is not None else None
            

class HealthDataResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["HealthData"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [HealthData(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class HealthData:
    synced_block_height: Optional[int]
    synced_block_signed_at: Optional[datetime]
    latest_block_height: Optional[int]
    latest_block_signed_at: Optional[datetime]

    def __init__(self, data):
        self.synced_block_height = int(data["synced_block_height"]) if "synced_block_height" in data and data["synced_block_height"] is not None else None
        self.synced_block_signed_at = datetime.fromisoformat(data["synced_block_signed_at"]) if "synced_block_signed_at" in data and data["synced_block_signed_at"] is not None else None
        self.latest_block_height = int(data["latest_block_height"]) if "latest_block_height" in data and data["latest_block_height"] is not None else None
        self.latest_block_signed_at = datetime.fromisoformat(data["latest_block_signed_at"]) if "latest_block_signed_at" in data and data["latest_block_signed_at"] is not None else None


class XykService:
    __api_key: str
    __debug: Optional[bool]
    
    def __init__(self, api_key: str, debug: Optional[bool] = False):
        self.__api_key = api_key
        self.__debug = debug


    def get_pools(self, chain_name: chain, dex_name: str) -> Response[PoolResponse]:
        """
        Commonly used to get all the pools of a particular DEX. Supports most common DEXs (Uniswap, SushiSwap, etc), and returns detailed trading data (volume, liquidity, swap counts, fees, LP token prices).

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        (str): The DEX name eg: `uniswap_v2`.
        """
        success = False
        data: Optional[Response[PoolResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/{dex_name}/pools/", params=url_params, headers={
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

                data_class = PoolResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_dex_for_pool_address(self, chain_name: chain, pool_address: str) -> Response[PoolToDexResponse]:
        """
        Commonly used to get the corresponding supported DEX given a pool address, along with the swap fees, DEX's logo url, and factory addresses. Useful to identifying the specific DEX to which a pair address is associated.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        pool_address (str): The requested pool address.
        """
        success = False
        data: Optional[Response[PoolToDexResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/address/{pool_address}/dex_name/", params=url_params, headers={
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

                data_class = PoolToDexResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_pool_by_address(self, chain_name: chain, dex_name: str, pool_address: str) -> Response[PoolByAddressResponse]:
        """
        Commonly used to get the 7 day and 30 day time-series data (volume, liquidity, price) of a particular liquidity pool in a DEX. Useful for building time-series charts on DEX trading activity.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        dex_name (str): The DEX name eg: `uniswap_v2`.
        pool_address (str): The pool contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        """
        success = False
        data: Optional[Response[PoolByAddressResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/{dex_name}/pools/address/{pool_address}/", params=url_params, headers={
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

                data_class = PoolByAddressResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_pools_for_token_address(self, chain_name: chain, token_address: str, page: int, quote_currency: Optional[quote] = None, dex_name: Optional[str] = None) -> Response[PoolsDexDataResponse]:
        """
        Commonly used to get all pools and the supported DEX for a token. Useful for building a table of top pairs across all supported DEXes that the token is trading on.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        token_address (str): The token contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        page (int): The requested 0-indexed page number.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        """
        success = False
        data: Optional[Response[PoolsDexDataResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                
                if dex_name is not None:
                    url_params["dex-name"] = str(dex_name)
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/tokens/address/{token_address}/pools/page/{page}/", params=url_params, headers={
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

                data_class = PoolsDexDataResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_address_exchange_balances(self, chain_name: chain, dex_name: str, account_address: str) -> Response[AddressExchangeBalancesResponse]:
        """
        Commonly used to return balance of a wallet/contract address on a specific DEX.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        dex_name (str): The DEX name eg: `uniswap_v2`.
        account_address (str): The account address.
        """
        success = False
        data: Optional[Response[AddressExchangeBalancesResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/{dex_name}/address/{account_address}/balances/", params=url_params, headers={
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

                data_class = AddressExchangeBalancesResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_pools_for_wallet_address(self, chain_name: chain, wallet_address: str, page: int, token_address: Optional[str] = None, quote_currency: Optional[quote] = None, dex_name: Optional[str] = None) -> Response[PoolsDexDataResponse]:
        """
        Commonly used to get all pools and supported DEX for a wallet. Useful for building a personal DEX UI showcasing pairs and supported DEXes associated to the wallet.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The account address.
        page (int): The requested 0-indexed page number.
        token_address (str): The token contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        """
        success = False
        data: Optional[Response[PoolsDexDataResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if token_address is not None:
                    url_params["token-address"] = str(token_address)
                    
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                
                if dex_name is not None:
                    url_params["dex-name"] = str(dex_name)
                    

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/address/{wallet_address}/pools/page/{page}/", params=url_params, headers={
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

                data_class = PoolsDexDataResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_network_exchange_tokens(self, chain_name: chain, dex_name: str) -> Response[NetworkExchangeTokensResponse]:
        """
        Commonly used to retrieve all network exchange tokens for a specific DEX. Useful for building a top tokens table by total liquidity within a particular DEX.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        dex_name (str): The DEX name eg: `uniswap_v2`.
        """
        success = False
        data: Optional[Response[NetworkExchangeTokensResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/{dex_name}/tokens/", params=url_params, headers={
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

                data_class = NetworkExchangeTokensResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_supported_dexes(self ) -> Response[SupportedDexesResponse]:
        """
        Commonly used to get all the supported DEXs available for the xy=k endpoints, along with the swap fees and factory addresses.

        Parameters:

        
        """
        success = False
        data: Optional[Response[SupportedDexesResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/xy=k/supported_dexes/", params=url_params, headers={
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

                data_class = SupportedDexesResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_single_network_exchange_token(self, chain_name: chain, dex_name: str, token_address: str) -> Response[SingleNetworkExchangeTokenResponse]:
        """
        Commonly used to get historical daily swap count for a single network exchange token.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        dex_name (str): The DEX name eg: `uniswap_v2`.
        token_address (str): The token contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        """
        success = False
        data: Optional[Response[SingleNetworkExchangeTokenResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/{dex_name}/tokens/address/{token_address}/", params=url_params, headers={
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

                data_class = SingleNetworkExchangeTokenResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_transactions_for_account_address(self, chain_name: chain, dex_name: str, account_address: str) -> Response[TransactionsForAccountAddressResponse]:
        """
        Commonly used to get all the DEX transactions of a wallet. Useful for building tables of DEX activity segmented by wallet.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        dex_name (str): The DEX name eg: `uniswap_v2`.
        account_address (str): The account address. Passing in an `ENS` or `RNS` resolves automatically.
        """
        success = False
        data: Optional[Response[TransactionsForAccountAddressResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/{dex_name}/address/{account_address}/transactions/", params=url_params, headers={
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

                data_class = TransactionsForAccountAddressResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_transactions_for_token_address(self, chain_name: chain, dex_name: str, token_address: str) -> Response[TransactionsForTokenAddressResponse]:
        """
        Commonly used to get all the transactions of a token within a particular DEX. Useful for getting a per-token view of DEX activity.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        dex_name (str): The DEX name eg: `uniswap_v2`.
        token_address (str): The token contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        """
        success = False
        data: Optional[Response[TransactionsForTokenAddressResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/{dex_name}/tokens/address/{token_address}/transactions/", params=url_params, headers={
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

                data_class = TransactionsForTokenAddressResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_transactions_for_exchange(self, chain_name: chain, dex_name: str, pool_address: str) -> Response[TransactionsForExchangeResponse]:
        """
        Commonly used for getting all the transactions of a particular DEX liquidity pool. Useful for building a transactions history table for an individual pool.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        dex_name (str): The DEX name eg: `uniswap_v2`.
        pool_address (str): The pool contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        """
        success = False
        data: Optional[Response[TransactionsForExchangeResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/{dex_name}/pools/address/{pool_address}/transactions/", params=url_params, headers={
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

                data_class = TransactionsForExchangeResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        
    def get_ecosystem_chart_data(self, chain_name: chain, dex_name: str) -> Response[EcosystemChartDataResponse]:
        """
        Commonly used to get a 7d and 30d time-series chart of DEX activity. Includes volume and swap count.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        dex_name (str): The DEX name eg: `uniswap_v2`.
        """
        success = False
        data: Optional[Response[EcosystemChartDataResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/{dex_name}/ecosystem/", params=url_params, headers={
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

                data_class = EcosystemChartDataResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
        return Response (
            data=None,
            error=True,
            error_code=500,
            error_message="Internal server error"
        )
        
    def get_health_data(self, chain_name: chain, dex_name: str) -> Response[HealthDataResponse]:
        """
        Commonly used to ping the health of xy=k endpoints to get the synced block height per chain.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        dex_name (str): The DEX name eg: `uniswap_v2`.
        """
        success = False
        data: Optional[Response[HealthDataResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/xy=k/{dex_name}/health/", params=url_params, headers={
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

                data_class = HealthDataResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
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
