from datetime import datetime
from typing import AsyncIterable, List, Optional
import requests
from .util.back_off import ExponentialBackoff
from .util.api_helper import check_and_modify_response, paginate_endpoint, Response
from .util.types import chain, quote, user_agent
from .util.debugger import debug_output

class BalancesResponse:
    address: str
    """ The requested address. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    quote_currency: str
    """ The requested quote currency eg: `USD`. """
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    items: List["BalanceItem"]
    """ List of response items. """

    def __init__(self, data):
        self.address = data["address"]
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.quote_currency = data["quote_currency"]
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.items = [BalanceItem(item_data) for item_data in data["items"]]

class BalanceItem:
    contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    contract_display_name: Optional[str]
    """ A display-friendly name for the contract. """
    supports_erc: Optional[List[str]]
    """ A list of supported standard ERC interfaces, eg: `ERC20` and `ERC721`. """
    logo_url: Optional[str]
    """ The contract logo URL. """
    logo_urls: Optional["LogoUrls"]
    """ The balance item logo URLs. """
    last_transferred_at: Optional[datetime]
    """ The timestamp when the token was transferred. """
    native_token: Optional[bool]
    """ Indicates if a token is the chain's native gas token, eg: ETH on Ethereum. """
    type: Optional[str]
    """ One of `cryptocurrency`, `stablecoin`, `nft` or `dust`. """
    is_spam: Optional[bool]
    """ Denotes whether the token is suspected spam. """
    balance: Optional[int]
    """ The asset balance. Use `contract_decimals` to scale this balance for display purposes. """
    balance_24h: Optional[int]
    """ The 24h asset balance. Use `contract_decimals` to scale this balance for display purposes. """
    quote_rate: Optional[float]
    """ The exchange rate for the requested quote currency. """
    quote_rate_24h: Optional[float]
    """ The 24h exchange rate for the requested quote currency. """
    quote: Optional[float]
    """ The current balance converted to fiat in `quote-currency`. """
    quote_24h: Optional[float]
    """ The 24h balance converted to fiat in `quote-currency`. """
    pretty_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """
    pretty_quote_24h: Optional[str]
    """ A prettier version of the 24h quote for rendering purposes. """
    protocol_metadata: Optional["ProtocolMetadata"]
    """ The protocol metadata. """
    nft_data: Optional[List["NftData"]]
    """ NFT-specific data. """

    def __init__(self, data):
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.contract_display_name = data["contract_display_name"] if "contract_display_name" in data and data["contract_display_name"] is not None else None
        self.supports_erc = data["supports_erc"] if "supports_erc" in data and data["supports_erc"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.last_transferred_at = datetime.fromisoformat(data["last_transferred_at"]) if "last_transferred_at" in data and data["last_transferred_at"] is not None else None
        self.native_token = data["native_token"] if "native_token" in data and data["native_token"] is not None else None
        self.type = data["type"] if "type" in data and data["type"] is not None else None
        self.is_spam = data["is_spam"] if "is_spam" in data and data["is_spam"] is not None else None
        self.balance = int(data["balance"]) if "balance" in data and data["balance"] is not None else None
        self.balance_24h = int(data["balance_24h"]) if "balance_24h" in data and data["balance_24h"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
        self.quote_rate_24h = data["quote_rate_24h"] if "quote_rate_24h" in data and data["quote_rate_24h"] is not None else None
        self.quote = data["quote"] if "quote" in data and data["quote"] is not None else None
        self.quote_24h = data["quote_24h"] if "quote_24h" in data and data["quote_24h"] is not None else None
        self.pretty_quote = data["pretty_quote"] if "pretty_quote" in data and data["pretty_quote"] is not None else None
        self.pretty_quote_24h = data["pretty_quote_24h"] if "pretty_quote_24h" in data and data["pretty_quote_24h"] is not None else None
        self.logo_urls = LogoUrls(data["logo_urls"]) if "logo_urls" in data and data["logo_urls"] is not None else None
        self.protocol_metadata = ProtocolMetadata(data["protocol_metadata"]) if "protocol_metadata" in data and data["protocol_metadata"] is not None else None
        self.nft_data = [NftData(item_data) for item_data in data["nft_data"]] if "nft_data" in data and data["nft_data"] is not None else None

class LogoUrls:
    token_logo_url: Optional[str]
    """ The token logo URL. """
    protocol_logo_url: Optional[str]
    """ The protocol logo URL. """
    chain_logo_url: Optional[str]
    """ The chain logo URL. """

    def __init__(self, data):
        self.token_logo_url = data["token_logo_url"] if "token_logo_url" in data and data["token_logo_url"] is not None else None
        self.protocol_logo_url = data["protocol_logo_url"] if "protocol_logo_url" in data and data["protocol_logo_url"] is not None else None
        self.chain_logo_url = data["chain_logo_url"] if "chain_logo_url" in data and data["chain_logo_url"] is not None else None

class ProtocolMetadata:
    protocol_name: Optional[str]
    """ The name of the protocol. """

    def __init__(self, data):
        self.protocol_name = data["protocol_name"] if "protocol_name" in data and data["protocol_name"] is not None else None
   
class NftData:
    token_id: Optional[int]
    """ The token's id. """
    token_url: Optional[str]
    original_owner: Optional[str]
    """ The original minter. """
    external_data: Optional["NftExternalData"]
    asset_cached: Optional[bool]
    """ If `true`, the asset data is available from the Covalent CDN. """
    image_cached: Optional[bool]
    """ If `true`, the image data is available from the Covalent CDN. """

    def __init__(self, data):
        self.token_id = int(data["token_id"]) if "token_id" in data and data["token_id"] is not None else None
        self.token_url = data["token_url"] if "token_url" in data and data["token_url"] is not None else None
        self.original_owner = data["original_owner"] if "original_owner" in data and data["original_owner"] is not None else None
        self.asset_cached = data["asset_cached"] if "asset_cached" in data and data["asset_cached"] is not None else None
        self.image_cached = data["image_cached"] if "image_cached" in data and data["image_cached"] is not None else None
        self.external_data = NftExternalData(data["external_data"]) if "external_data" in data and data["external_data"] is not None else None

class NftExternalData:
    name: Optional[str]
    description: Optional[str]
    asset_url: Optional[str]
    asset_file_extension: Optional[str]
    asset_mime_type: Optional[str]
    asset_size_bytes: Optional[str]
    image: Optional[str]
    image_256: Optional[str]
    image_512: Optional[str]
    image_1024: Optional[str]
    animation_url: Optional[str]
    external_url: Optional[str]
    attributes: Optional[List["NftCollectionAttribute"]]

    def __init__(self, data):
        self.name = data["name"] if "name" in data and data["name"] is not None else None
        self.description = data["description"] if "description" in data and data["description"] is not None else None
        self.asset_url = data["asset_url"] if "asset_url" in data and data["asset_url"] is not None else None
        self.asset_file_extension = data["asset_file_extension"] if "asset_file_extension" in data and data["asset_file_extension"] is not None else None
        self.asset_mime_type = data["asset_mime_type"] if "asset_mime_type" in data and data["asset_mime_type"] is not None else None
        self.asset_size_bytes = data["asset_size_bytes"] if "asset_size_bytes" in data and data["asset_size_bytes"] is not None else None
        self.image = data["image"] if "image" in data and data["image"] is not None else None
        self.image_256 = data["image_256"] if "image_256" in data and data["image_256"] is not None else None
        self.image_512 = data["image_512"] if "image_512" in data and data["image_512"] is not None else None
        self.image_1024 = data["image_1024"] if "image_1024" in data and data["image_1024"] is not None else None
        self.animation_url = data["animation_url"] if "animation_url" in data and data["animation_url"] is not None else None
        self.external_url = data["external_url"] if "external_url" in data and data["external_url"] is not None else None
        self.attributes = [NftCollectionAttribute(item_data) for item_data in data["attributes"]] if "attributes" in data and data["attributes"] is not None else None

class NftCollectionAttribute:
    trait_type: Optional[str]
    value: Optional[str]

    def __init__(self, data):
        self.trait_type = data["trait_type"] if "trait_type" in data and data["trait_type"] is not None else None
        self.value = data["value"] if "value" in data and data["value"] is not None else None
            

class PortfolioResponse:
    address: str
    """ The requested address. """
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    quote_currency: str
    """ The requested quote currency eg: `USD`. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["PortfolioItem"]
    """ List of response items. """

    def __init__(self, data):
        self.address = data["address"]
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.quote_currency = data["quote_currency"]
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [PortfolioItem(item_data) for item_data in data["items"]]

class PortfolioItem:
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    logo_url: Optional[str]
    """ The contract logo URL. """
    holdings: Optional[List["HoldingItem"]]

    def __init__(self, data):
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.holdings = [HoldingItem(item_data) for item_data in data["holdings"]] if "holdings" in data and data["holdings"] is not None else None

class HoldingItem:
    quote_rate: Optional[float]
    """ The exchange rate for the requested quote currency. """
    timestamp: Optional[datetime]
    close: Optional["OhlcItem"]
    high: Optional["OhlcItem"]
    low: Optional["OhlcItem"]
    open: Optional["OhlcItem"]

    def __init__(self, data):
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
        self.timestamp = datetime.fromisoformat(data["timestamp"]) if "timestamp" in data and data["timestamp"] is not None else None
        self.close = OhlcItem(data["close"]) if "close" in data and data["close"] is not None else None
        self.high = OhlcItem(data["high"]) if "high" in data and data["high"] is not None else None
        self.low = OhlcItem(data["low"]) if "low" in data and data["low"] is not None else None
        self.open = OhlcItem(data["open"]) if "open" in data and data["open"] is not None else None

class OhlcItem:
    balance: Optional[int]
    """ The asset balance. Use `contract_decimals` to scale this balance for display purposes. """
    quote: Optional[float]
    """ The current balance converted to fiat in `quote-currency`. """
    pretty_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """

    def __init__(self, data):
        self.balance = int(data["balance"]) if "balance" in data and data["balance"] is not None else None
        self.quote = data["quote"] if "quote" in data and data["quote"] is not None else None
        self.pretty_quote = data["pretty_quote"] if "pretty_quote" in data and data["pretty_quote"] is not None else None
            

class Erc20TransfersResponse:
    address: str
    """ The requested address. """
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    quote_currency: str
    """ The requested quote currency eg: `USD`. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["BlockTransactionWithContractTransfers"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.address = data["address"]
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.quote_currency = data["quote_currency"]
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [BlockTransactionWithContractTransfers(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class BlockTransactionWithContractTransfers:
    block_signed_at: Optional[datetime]
    """ The block signed timestamp in UTC. """
    block_height: Optional[int]
    """ The height of the block. """
    tx_hash: Optional[str]
    """ The requested transaction hash. """
    tx_offset: Optional[int]
    """ The offset is the position of the tx in the block. """
    successful: Optional[bool]
    """ Whether or not transaction is successful. """
    from_address: Optional[str]
    """ The sender's wallet address. """
    from_address_label: Optional[str]
    """ The label of `from` address. """
    to_address: Optional[str]
    """ The receiver's wallet address. """
    to_address_label: Optional[str]
    """ The label of `to` address. """
    value: Optional[int]
    """ The value attached to this tx. """
    value_quote: Optional[float]
    """ The value attached in `quote-currency` to this tx. """
    pretty_value_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """
    gas_offered: Optional[int]
    gas_spent: Optional[int]
    """ The gas spent for this tx. """
    gas_price: Optional[int]
    """ The gas price at the time of this tx. """
    fees_paid: Optional[int]
    """ The transaction's gas_price * gas_spent, denoted in wei. """
    gas_quote: Optional[float]
    """ The gas spent in `quote-currency` denomination. """
    pretty_gas_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """
    gas_quote_rate: Optional[float]
    """ The native gas exchange rate for the requested `quote-currency`. """
    transfers: Optional[List["TokenTransferItem"]]

    def __init__(self, data):
        self.block_signed_at = datetime.fromisoformat(data["block_signed_at"]) if "block_signed_at" in data and data["block_signed_at"] is not None else None
        self.block_height = int(data["block_height"]) if "block_height" in data and data["block_height"] is not None else None
        self.tx_hash = data["tx_hash"] if "tx_hash" in data and data["tx_hash"] is not None else None
        self.tx_offset = int(data["tx_offset"]) if "tx_offset" in data and data["tx_offset"] is not None else None
        self.successful = data["successful"] if "successful" in data and data["successful"] is not None else None
        self.from_address = data["from_address"] if "from_address" in data and data["from_address"] is not None else None
        self.from_address_label = data["from_address_label"] if "from_address_label" in data and data["from_address_label"] is not None else None
        self.to_address = data["to_address"] if "to_address" in data and data["to_address"] is not None else None
        self.to_address_label = data["to_address_label"] if "to_address_label" in data and data["to_address_label"] is not None else None
        self.value = int(data["value"]) if "value" in data and data["value"] is not None else None
        self.value_quote = data["value_quote"] if "value_quote" in data and data["value_quote"] is not None else None
        self.pretty_value_quote = data["pretty_value_quote"] if "pretty_value_quote" in data and data["pretty_value_quote"] is not None else None
        self.gas_offered = int(data["gas_offered"]) if "gas_offered" in data and data["gas_offered"] is not None else None
        self.gas_spent = int(data["gas_spent"]) if "gas_spent" in data and data["gas_spent"] is not None else None
        self.gas_price = int(data["gas_price"]) if "gas_price" in data and data["gas_price"] is not None else None
        self.fees_paid = int(data["fees_paid"]) if "fees_paid" in data and data["fees_paid"] is not None else None
        self.gas_quote = data["gas_quote"] if "gas_quote" in data and data["gas_quote"] is not None else None
        self.pretty_gas_quote = data["pretty_gas_quote"] if "pretty_gas_quote" in data and data["pretty_gas_quote"] is not None else None
        self.gas_quote_rate = data["gas_quote_rate"] if "gas_quote_rate" in data and data["gas_quote_rate"] is not None else None
        self.transfers = [TokenTransferItem(item_data) for item_data in data["transfers"]] if "transfers" in data and data["transfers"] is not None else None

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
            

class TokenTransferItem:
    block_signed_at: Optional[datetime]
    """ The block signed timestamp in UTC. """
    tx_hash: Optional[str]
    """ The requested transaction hash. """
    from_address: Optional[str]
    """ The sender's wallet address. """
    from_address_label: Optional[str]
    """ The label of `from` address. """
    to_address: Optional[str]
    """ The receiver's wallet address. """
    to_address_label: Optional[str]
    """ The label of `to` address. """
    contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    logo_url: Optional[str]
    """ The contract logo URL. """
    transfer_type: Optional[str]
    """ Categorizes token transactions as either `transfer-in` or `transfer-out`, indicating whether tokens are being received or sent from an account. """
    delta: Optional[int]
    """ The delta attached to this transfer. """
    balance: Optional[int]
    """ The asset balance. Use `contract_decimals` to scale this balance for display purposes. """
    quote_rate: Optional[float]
    """ The exchange rate for the requested quote currency. """
    delta_quote: Optional[float]
    """ The current delta converted to fiat in `quote-currency`. """
    pretty_delta_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """
    balance_quote: Optional[float]
    """ The current balance converted to fiat in `quote-currency`. """
    method_calls: Optional[List["MethodCallsForTransfers"]]
    """ Additional details on which transfer events were invoked. Defaults to `true`. """

    def __init__(self, data):
        self.block_signed_at = datetime.fromisoformat(data["block_signed_at"]) if "block_signed_at" in data and data["block_signed_at"] is not None else None
        self.tx_hash = data["tx_hash"] if "tx_hash" in data and data["tx_hash"] is not None else None
        self.from_address = data["from_address"] if "from_address" in data and data["from_address"] is not None else None
        self.from_address_label = data["from_address_label"] if "from_address_label" in data and data["from_address_label"] is not None else None
        self.to_address = data["to_address"] if "to_address" in data and data["to_address"] is not None else None
        self.to_address_label = data["to_address_label"] if "to_address_label" in data and data["to_address_label"] is not None else None
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.transfer_type = data["transfer_type"] if "transfer_type" in data and data["transfer_type"] is not None else None
        self.delta = int(data["delta"]) if "delta" in data and data["delta"] is not None else None
        self.balance = int(data["balance"]) if "balance" in data and data["balance"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
        self.delta_quote = data["delta_quote"] if "delta_quote" in data and data["delta_quote"] is not None else None
        self.pretty_delta_quote = data["pretty_delta_quote"] if "pretty_delta_quote" in data and data["pretty_delta_quote"] is not None else None
        self.balance_quote = data["balance_quote"] if "balance_quote" in data and data["balance_quote"] is not None else None
        self.method_calls = [MethodCallsForTransfers(item_data) for item_data in data["method_calls"]] if "method_calls" in data and data["method_calls"] is not None else None

class MethodCallsForTransfers:
    sender_address: Optional[str]
    """ The address of the sender. """
    method: Optional[str]

    def __init__(self, data):
        self.sender_address = data["sender_address"] if "sender_address" in data and data["sender_address"] is not None else None
        self.method = data["method"] if "method" in data and data["method"] is not None else None
            

class TokenHoldersResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["TokenHolder"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [TokenHolder(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class TokenHolder:
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
    address: Optional[str]
    """ The requested address. """
    balance: Optional[int]
    """ The asset balance. Use `contract_decimals` to scale this balance for display purposes. """
    total_supply: Optional[int]
    """ Total supply of this token. """
    block_height: Optional[int]
    """ The height of the block. """

    def __init__(self, data):
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.supports_erc = data["supports_erc"] if "supports_erc" in data and data["supports_erc"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.address = data["address"] if "address" in data and data["address"] is not None else None
        self.balance = int(data["balance"]) if "balance" in data and data["balance"] is not None else None
        self.total_supply = int(data["total_supply"]) if "total_supply" in data and data["total_supply"] is not None else None
        self.block_height = int(data["block_height"]) if "block_height" in data and data["block_height"] is not None else None          

class HistoricalBalancesResponse:
    address: str
    """ The requested address. """
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    quote_currency: str
    """ The requested quote currency eg: `USD`. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["HistoricalBalanceItem"]
    """ List of response items. """

    def __init__(self, data):
        self.address = data["address"]
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.quote_currency = data["quote_currency"]
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [HistoricalBalanceItem(item_data) for item_data in data["items"]]

class HistoricalBalanceItem:
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
    block_height: Optional[int]
    """ The height of the block. """
    last_transferred_block_height: Optional[int]
    """ The block height when the token was last transferred. """
    last_transferred_at: Optional[datetime]
    """ The timestamp when the token was transferred. """
    native_token: Optional[bool]
    """ Indicates if a token is the chain's native gas token, eg: ETH on Ethereum. """
    type: Optional[str]
    """ One of `cryptocurrency`, `stablecoin`, `nft` or `dust`. """
    is_spam: Optional[bool]
    """ Denotes whether the token is suspected spam. """
    balance: Optional[int]
    """ The asset balance. Use `contract_decimals` to scale this balance for display purposes. """
    quote_rate: Optional[float]
    """ The exchange rate for the requested quote currency. """
    quote: Optional[float]
    """ The current balance converted to fiat in `quote-currency`. """
    pretty_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """
    nft_data: Optional[List["NftData"]]
    """ NFT-specific data. """

    def __init__(self, data):
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.supports_erc = data["supports_erc"] if "supports_erc" in data and data["supports_erc"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.block_height = int(data["block_height"]) if "block_height" in data and data["block_height"] is not None else None
        self.last_transferred_block_height = int(data["last_transferred_block_height"]) if "last_transferred_block_height" in data and data["last_transferred_block_height"] is not None else None
        self.last_transferred_at = datetime.fromisoformat(data["last_transferred_at"]) if "last_transferred_at" in data and data["last_transferred_at"] is not None else None
        self.native_token = data["native_token"] if "native_token" in data and data["native_token"] is not None else None
        self.type = data["type"] if "type" in data and data["type"] is not None else None
        self.is_spam = data["is_spam"] if "is_spam" in data and data["is_spam"] is not None else None
        self.balance = int(data["balance"]) if "balance" in data and data["balance"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
        self.quote = data["quote"] if "quote" in data and data["quote"] is not None else None
        self.pretty_quote = data["pretty_quote"] if "pretty_quote" in data and data["pretty_quote"] is not None else None
        self.nft_data = [NftData(item_data) for item_data in data["nft_data"]] if "nft_data" in data and data["nft_data"] is not None else None  
        
class TokenBalanceNativeResponse:
    address: str
    """ The requested address. """
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    quote_currency: str
    """ The requested quote currency eg: `USD`. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["NativeBalanceItem"]
    """ List of response items. """

    def __init__(self, data):
        self.address = data["address"]
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.quote_currency = data["quote_currency"]
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [NativeBalanceItem(item_data) for item_data in data["items"]]

class NativeBalanceItem:
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
    block_height: Optional[int]
    """ The height of the block. """
    balance: Optional[int]
    """ The asset balance. Use `contract_decimals` to scale this balance for display purposes. """
    quote_rate: Optional[float]
    """ The exchange rate for the requested quote currency. """
    quote: Optional[float]
    """ The current balance converted to fiat in `quote-currency`. """
    pretty_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """

    def __init__(self, data):
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.supports_erc = data["supports_erc"] if "supports_erc" in data and data["supports_erc"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.block_height = int(data["block_height"]) if "block_height" in data and data["block_height"] is not None else None
        self.balance = int(data["balance"]) if "balance" in data and data["balance"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
        self.quote = data["quote"] if "quote" in data and data["quote"] is not None else None
        self.pretty_quote = data["pretty_quote"] if "pretty_quote" in data and data["pretty_quote"] is not None else None
                  

class BalanceService:
    __api_key: str
    __debug: Optional[bool]
    def __init__(self, api_key: str, debug: Optional[bool] = False):
        self.__api_key = api_key
        self.__debug = debug


    def get_token_balances_for_wallet_address(self, chain_name: chain, wallet_address: str, quote_currency: Optional[quote] = None, nft: Optional[bool] = None, no_nft_fetch: Optional[bool] = None, no_spam: Optional[bool] = None, no_nft_asset_metadata: Optional[bool] = None) -> Response[BalancesResponse]:
        """
        Commonly used to fetch the native, fungible (ERC20), and non-fungible (ERC721 & ERC1155) tokens held by an address. Response includes spot prices and other metadata.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        nft (bool): If `true`, NFTs will be included in the response.
        no_nft_fetch (bool): If `true`, only NFTs that have been cached will be included in the response. Helpful for faster response times.
        no_spam (bool): If `true`, the suspected spam tokens are removed. Supports `eth-mainnet` and `matic-mainnet`.
        no_nft_asset_metadata (bool): If `true`, the response shape is limited to a list of collections and token ids, omitting metadata and asset information. Helpful for faster response times and wallets holding a large number of NFTs.
        """
        success = False
        data: Optional[Response[BalancesResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                    
                if nft is not None:
                    url_params["nft"] = str(nft)
                    
                if no_nft_fetch is not None:
                    url_params["no-nft-fetch"] = str(no_nft_fetch)
                    
                if no_spam is not None:
                    url_params["no-spam"] = str(no_spam)
                    
                if no_nft_asset_metadata is not None:
                    url_params["no-nft-asset-metadata"] = str(no_nft_asset_metadata)  

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/balances_v2/", params=url_params, headers={
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
    
                data_class = BalancesResponse(data.data)
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
        
    def get_historical_portfolio_for_wallet_address(self, chain_name: chain, wallet_address: str, quote_currency: Optional[quote] = None, days: Optional[int] = None) -> Response[PortfolioResponse]:
        """
        Commonly used to render a daily portfolio balance for an address broken down by the token. The timeframe is user-configurable, defaults to 30 days.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        days (int): The number of days to return data for. Defaults to 30 days.
        """
        success = False
        data: Optional[Response[PortfolioResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                    
                if days is not None:
                    url_params["days"] = str(days)
                    

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/portfolio_v2/", params=url_params, headers={
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
                
                data_class = PortfolioResponse(data.data)
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
        
    async def get_erc20_transfers_for_wallet_address(self, chain_name: chain, wallet_address: str, quote_currency: Optional[quote] = None, contract_address: Optional[str] = None, starting_block: Optional[int] = None, ending_block: Optional[int] = None, page_size: Optional[int] = None, page_number: Optional[int] = None) -> AsyncIterable[BlockTransactionWithContractTransfers]:
        """
        Commonly used to render the transfer-in and transfer-out of a token along with historical prices from an address.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        contract_address (str): The requested contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        starting_block (int): The block height to start from, defaults to `0`.
        ending_block (int): The block height to end at, defaults to current block height.
        page_size (int): Number of items per page. Omitting this parameter defaults to 100.
        page_number (int): 0-indexed page number to begin pagination.
        """
        success = False
        response = None
        while not success:
            try:
                url_params = {}
                
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                
                if contract_address is not None:
                    url_params["contract-address"] = str(contract_address)
                
                if starting_block is not None:
                    url_params["starting-block"] = str(starting_block)
                
                if ending_block is not None:
                    url_params["ending-block"] = str(ending_block)
                
                if page_size is not None:
                    url_params["page-size"] = str(page_size)
                
                if page_number is not None:
                    url_params["page-number"] = str(page_number)
                

                async for response in paginate_endpoint(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/transfers_v2/", self.__api_key, url_params, BlockTransactionWithContractTransfers, self.__debug):
                    yield response

                success = True
            except Exception as error:
                success = True
                raise Exception(error)
            
    def get_erc20_transfers_for_wallet_address_by_page(self, chain_name: chain, wallet_address: str, quote_currency: Optional[quote] = None, contract_address: Optional[str] = None, starting_block: Optional[int] = None, ending_block: Optional[int] = None, page_size: Optional[int] = None, page_number: Optional[int] = None) -> Response[Erc20TransfersResponse]:
        """
        Commonly used to render the transfer-in and transfer-out of a token along with historical prices from an address.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        contract_address (str): The requested contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        starting_block (int): The block height to start from, defaults to `0`.
        ending_block (int): The block height to end at, defaults to current block height.
        page_size (int): Number of items per page. Omitting this parameter defaults to 100.
        page_number (int): 0-indexed page number to begin pagination.
        """
        success = False
        data: Optional[Response[Erc20TransfersResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                
                if contract_address is not None:
                    url_params["contract-address"] = str(contract_address)
                
                if starting_block is not None:
                    url_params["starting-block"] = str(starting_block)
                
                if ending_block is not None:
                    url_params["ending-block"] = str(ending_block)
                
                if page_size is not None:
                    url_params["page-size"] = str(page_size)
                
                if page_number is not None:
                    url_params["page-number"] = str(page_number)
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/transfers_v2/", params=url_params, headers={
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
                
                data_class = Erc20TransfersResponse(data.data)
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
        
    async def get_token_holders_v2_for_token_address(self, chain_name: chain, token_address: str, block_height: Optional[int] = None, date: Optional[str] = None, page_size: Optional[int] = None, page_number: Optional[int] = None) -> AsyncIterable[TokenHolder]:
        """
        Commonly used to get a list of all the token holders for a specified ERC20 or ERC721 token. Returns historic token holders when block-height is set (defaults to `latest`). Useful for building pie charts of token holders.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        token_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        block_height (int): Ending block to define a block range. Omitting this parameter defaults to the latest block height.
        date (str): Ending date to define a block range (YYYY-MM-DD). Omitting this parameter defaults to the current date.
        page_size (int): Number of items per page. Note: Currently, only values of `100` and `1000` are supported. Omitting this parameter defaults to 100.
        page_number (int): 0-indexed page number to begin pagination.
        """
        success = False
        response = None
        while not success:
            try:
                url_params = {}
                
                if block_height is not None:
                    url_params["block-height"] = str(block_height)
                
                if page_size is not None:
                    url_params["page-size"] = str(page_size)
                
                if page_number is not None:
                    url_params["page-number"] = str(page_number)
                
                if date is not None:
                    url_params["date"] = str(date)
                

                async for response in paginate_endpoint(f"https://api.covalenthq.com/v1/{chain_name}/tokens/{token_address}/token_holders_v2/", self.__api_key, url_params, TokenHolder, self.__debug):
                    yield response

                success = True
            except Exception as error:
                success = True
                raise Exception(error)
            
    def get_token_holders_v2_for_token_address_by_page(self, chain_name: chain, token_address: str, block_height: Optional[int] = None, date: Optional[str] = None, page_size: Optional[int] = None, page_number: Optional[int] = None) -> Response[TokenHoldersResponse]:
        """
        Commonly used to get a list of all the token holders for a specified ERC20 or ERC721 token. Returns historic token holders when block-height is set (defaults to `latest`). Useful for building pie charts of token holders.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        token_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        block_height (int): Ending block to define a block range. Omitting this parameter defaults to the latest block height.
        date (str): Ending date to define a block range (YYYY-MM-DD). Omitting this parameter defaults to the current date.
        page_size (int): Number of items per page. Note: Currently, only values of `100` and `1000` are supported. Omitting this parameter defaults to 100.
        page_number (int): 0-indexed page number to begin pagination.
        """
        success = False
        data: Optional[Response[TokenHoldersResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if block_height is not None:
                    url_params["block-height"] = str(block_height)
                
                if page_size is not None:
                    url_params["page-size"] = str(page_size)
                
                if page_number is not None:
                    url_params["page-number"] = str(page_number)
                
                if date is not None:
                    url_params["date"] = str(date)
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/tokens/{token_address}/token_holders_v2/", params=url_params, headers={
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
                
                data_class = TokenHoldersResponse(data.data)
                check_and_modify_response(data_class)
                success = True
                return Response(
                    data=data_class,
                    error=data.error,
                    error_code=data.error_code if data else response.status_code,
                    error_message=data.error_message if data else "Internal server error" if response.status_code == 500 else "401 Authorization Required"
                )
            except Exception as error:
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
        
    def get_historical_token_balances_for_wallet_address(self, chain_name: chain, wallet_address: str, quote_currency: Optional[quote] = None, nft: Optional[bool] = None, no_nft_fetch: Optional[bool] = None, no_spam: Optional[bool] = None, no_nft_asset_metadata: Optional[bool] = None, block_height: Optional[int] = None, date: Optional[str] = None) -> Response[HistoricalBalancesResponse]:
        """
        Commonly used to fetch the historical native, fungible (ERC20), and non-fungible (ERC721 & ERC1155) tokens held by an address at a given block height or date. Response includes daily prices and other metadata.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        nft (bool): If `true`, NFTs will be included in the response.
        no_nft_fetch (bool): If `true`, only NFTs that have been cached will be included in the response. Helpful for faster response times.
        no_spam (bool): If `true`, the suspected spam tokens are removed. Supports `eth-mainnet` and `matic-mainnet`.
        no_nft_asset_metadata (bool): If `true`, the response shape is limited to a list of collections and token ids, omitting metadata and asset information. Helpful for faster response times and wallets holding a large number of NFTs.
        block_height (int): Ending block to define a block range. Omitting this parameter defaults to the latest block height.
        date (str): Ending date to define a block range (YYYY-MM-DD). Omitting this parameter defaults to the current date.
        """
        success = False
        data: Optional[Response[HistoricalBalancesResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                    
                if nft is not None:
                    url_params["nft"] = str(nft)
                    
                if no_nft_fetch is not None:
                    url_params["no-nft-fetch"] = str(no_nft_fetch)
                    
                if no_spam is not None:
                    url_params["no-spam"] = str(no_spam)
                    
                if no_nft_asset_metadata is not None:
                    url_params["no-nft-asset-metadata"] = str(no_nft_asset_metadata)
                    
                if block_height is not None:
                    url_params["block-height"] = str(block_height)
                    
                if date is not None:
                    url_params["date"] = str(date)  

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/historical_balances/", params=url_params, headers={
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
                
                data_class = HistoricalBalancesResponse(data.data)
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
        
    def get_native_token_balance(self, chain_name: chain, wallet_address: str, quote_currency: Optional[quote] = None, block_height: Optional[int] = None) -> Response[TokenBalanceNativeResponse]:
        """
        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        block_height (int): Ending block to define a block range. Omitting this parameter defaults to the latest block height.
        """
        success = False
        data: Optional[Response[TokenBalanceNativeResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                    
                if block_height is not None:
                    url_params["block-height"] = str(block_height)
                    
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/balances_native/", params=url_params, headers={
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

                data_class = TokenBalanceNativeResponse(data.data)
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

        