from datetime import datetime
from typing import AsyncIterable, List, Optional
import requests
from .util.back_off import ExponentialBackoff
from .util.api_helper import check_and_modify_response, paginate_endpoint, Response
from .util.types import chain, quote, user_agent
from .util.debugger import debug_output


class ChainCollectionResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["ChainCollectionItem"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [ChainCollectionItem(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class ChainCollectionItem:
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    is_spam: Optional[bool]
    """ Denotes whether the token is suspected spam. Supports `eth-mainnet` and `matic-mainnet`. """
    token_total_supply: Optional[int]
    cached_metadata_count: Optional[int]
    cached_asset_count: Optional[int]
    last_scraped_at: Optional[datetime]

    def __init__(self, data):
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.is_spam = data["is_spam"] if "is_spam" in data and data["is_spam"] is not None else None
        self.token_total_supply = int(data["token_total_supply"]) if "token_total_supply" in data and data["token_total_supply"] is not None else None
        self.cached_metadata_count = int(data["cached_metadata_count"]) if "cached_metadata_count" in data and data["cached_metadata_count"] is not None else None
        self.cached_asset_count = int(data["cached_asset_count"]) if "cached_asset_count" in data and data["cached_asset_count"] is not None else None
        self.last_scraped_at = datetime.fromisoformat(data["last_scraped_at"]) if "last_scraped_at" in data and data["last_scraped_at"] is not None else None
            

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
            

class NftAddressBalanceNftResponse:
    address: str
    """ The requested address. """
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    items: List["NftTokenContractBalanceItem"]
    """ List of response items. """

    def __init__(self, data):
        self.address = data["address"]
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.items = [NftTokenContractBalanceItem(item_data) for item_data in data["items"]]

class NftTokenContractBalanceItem:
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    supports_erc: Optional[List[str]]
    """ A list of supported standard ERC interfaces, eg: `ERC20` and `ERC721`. """
    is_spam: Optional[bool]
    """ Denotes whether the token is suspected spam. Supports `eth-mainnet` and `matic-mainnet`. """
    last_transfered_at: Optional[datetime]
    balance: Optional[int]
    """ The asset balance. Use `contract_decimals` to scale this balance for display purposes. """
    balance_24h: Optional[int]
    type: Optional[str]
    floor_price_quote: Optional[float]
    """ The current floor price converted to fiat in `quote-currency`. The floor price is determined by the last minimum sale price within the last 30 days across all the supported markets where the collection is sold on. """
    pretty_floor_price_quote: Optional[str]
    """ A prettier version of the floor price quote for rendering purposes. """
    floor_price_native_quote: Optional[float]
    """ The current floor price in native currency. The floor price is determined by the last minimum sale price within the last 30 days across all the supported markets where the collection is sold on. """
    nft_data: Optional[List["NftData"]]

    def __init__(self, data):
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.supports_erc = data["supports_erc"] if "supports_erc" in data and data["supports_erc"] is not None else None
        self.is_spam = data["is_spam"] if "is_spam" in data and data["is_spam"] is not None else None
        self.last_transfered_at = datetime.fromisoformat(data["last_transfered_at"]) if "last_transfered_at" in data and data["last_transfered_at"] is not None else None
        self.balance = int(data["balance"]) if "balance" in data and data["balance"] is not None else None
        self.balance_24h = int(data["balance_24h"]) if "balance_24h" in data and data["balance_24h"] is not None else None
        self.type = data["type"] if "type" in data and data["type"] is not None else None
        self.floor_price_quote = data["floor_price_quote"] if "floor_price_quote" in data and data["floor_price_quote"] is not None else None
        self.pretty_floor_price_quote = data["pretty_floor_price_quote"] if "pretty_floor_price_quote" in data and data["pretty_floor_price_quote"] is not None else None
        self.floor_price_native_quote = data["floor_price_native_quote"] if "floor_price_native_quote" in data and data["floor_price_native_quote"] is not None else None
        self.nft_data = [NftData(item_data) for item_data in data["nft_data"]] if "nft_data" in data and data["nft_data"] is not None else None

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
            

class NftMetadataResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    items: List["NftTokenContract"]
    """ List of response items. """
    pagination: Optional["Pagination"]
    """ Pagination metadata. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.items = [NftTokenContract(item_data) for item_data in data["items"]]
        self.pagination = Pagination(data["pagination"]) if "pagination" in data and data["pagination"] is not None else None

class NftTokenContract:
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    is_spam: Optional[bool]
    """ Denotes whether the token is suspected spam. Supports `eth-mainnet` and `matic-mainnet`. """
    type: Optional[str]
    nft_data: Optional["NftData"]

    def __init__(self, data):
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.is_spam = data["is_spam"] if "is_spam" in data and data["is_spam"] is not None else None
        self.type = data["type"] if "type" in data and data["type"] is not None else None
        self.nft_data = NftData(data["nft_data"]) if "nft_data" in data and data["nft_data"] is not None else None

class NftTransactionsResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["NftTransaction"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [NftTransaction(item_data) for item_data in data["items"]]

class NftTransaction:
    contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    logo_url: Optional[str]
    """ The contract logo URL. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    supports_erc: Optional[List[str]]
    """ A list of supported standard ERC interfaces, eg: `ERC20` and `ERC721`. """
    nft_transactions: Optional[List["NftTransactionItem"]]
    is_spam: Optional[bool]
    """ Denotes whether the token is suspected spam. Supports `eth-mainnet` and `matic-mainnet`. """

    def __init__(self, data):
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.supports_erc = data["supports_erc"] if "supports_erc" in data and data["supports_erc"] is not None else None
        self.is_spam = data["is_spam"] if "is_spam" in data and data["is_spam"] is not None else None
        self.nft_transactions = [NftTransactionItem(item_data) for item_data in data["nft_transactions"]] if "nft_transactions" in data and data["nft_transactions"] is not None else None

class NftTransactionItem:
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
    gas_offered: Optional[str]
    gas_spent: Optional[str]
    """ The gas spent for this tx. """
    gas_price: Optional[str]
    """ The gas price at the time of this tx. """
    fees_paid: Optional[int]
    """ The total transaction fees (gas_price * gas_spent) paid for this tx, denoted in wei. """
    gas_quote: Optional[float]
    """ The gas spent in `quote-currency` denomination. """
    pretty_gas_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """
    gas_quote_rate: Optional[float]
    log_events: Optional[List["LogEvent"]]
    """ The log events. """

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
        self.gas_offered = data["gas_offered"] if "gas_offered" in data and data["gas_offered"] is not None else None
        self.gas_spent = data["gas_spent"] if "gas_spent" in data and data["gas_spent"] is not None else None
        self.gas_price = data["gas_price"] if "gas_price" in data and data["gas_price"] is not None else None
        self.fees_paid = int(data["fees_paid"]) if "fees_paid" in data and data["fees_paid"] is not None else None
        self.gas_quote = data["gas_quote"] if "gas_quote" in data and data["gas_quote"] is not None else None
        self.pretty_gas_quote = data["pretty_gas_quote"] if "pretty_gas_quote" in data and data["pretty_gas_quote"] is not None else None
        self.gas_quote_rate = data["gas_quote_rate"] if "gas_quote_rate" in data and data["gas_quote_rate"] is not None else None
        self.log_events = [LogEvent(item_data) for item_data in data["log_events"]] if "log_events" in data and data["log_events"] is not None else None

class LogEvent:
    block_signed_at: Optional[datetime]
    """ The block signed timestamp in UTC. """
    block_height: Optional[int]
    """ The height of the block. """
    tx_offset: Optional[int]
    """ The offset is the position of the tx in the block. """
    log_offset: Optional[int]
    """ The offset is the position of the log entry within an event log. """
    tx_hash: Optional[str]
    """ The requested transaction hash. """
    raw_log_topics: Optional[List[str]]
    """ The log topics in raw data. """
    sender_contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    sender_name: Optional[str]
    """ The name of the sender. """
    sender_contract_ticker_symbol: Optional[str]
    sender_address: Optional[str]
    """ The address of the sender. """
    sender_address_label: Optional[str]
    """ The label of the sender address. """
    sender_logo_url: Optional[str]
    """ The contract logo URL. """
    raw_log_data: Optional[str]
    """ The log events in raw. """
    decoded: Optional["DecodedItem"]
    """ The decoded item. """

    def __init__(self, data):
        self.block_signed_at = datetime.fromisoformat(data["block_signed_at"]) if "block_signed_at" in data and data["block_signed_at"] is not None else None
        self.block_height = int(data["block_height"]) if "block_height" in data and data["block_height"] is not None else None
        self.tx_offset = int(data["tx_offset"]) if "tx_offset" in data and data["tx_offset"] is not None else None
        self.log_offset = int(data["log_offset"]) if "log_offset" in data and data["log_offset"] is not None else None
        self.tx_hash = data["tx_hash"] if "tx_hash" in data and data["tx_hash"] is not None else None
        self.raw_log_topics = data["raw_log_topics"] if "raw_log_topics" in data and data["raw_log_topics"] is not None else None
        self.sender_contract_decimals = int(data["sender_contract_decimals"]) if "sender_contract_decimals" in data and data["sender_contract_decimals"] is not None else None
        self.sender_name = data["sender_name"] if "sender_name" in data and data["sender_name"] is not None else None
        self.sender_contract_ticker_symbol = data["sender_contract_ticker_symbol"] if "sender_contract_ticker_symbol" in data and data["sender_contract_ticker_symbol"] is not None else None
        self.sender_address = data["sender_address"] if "sender_address" in data and data["sender_address"] is not None else None
        self.sender_address_label = data["sender_address_label"] if "sender_address_label" in data and data["sender_address_label"] is not None else None
        self.sender_logo_url = data["sender_logo_url"] if "sender_logo_url" in data and data["sender_logo_url"] is not None else None
        self.raw_log_data = data["raw_log_data"] if "raw_log_data" in data and data["raw_log_data"] is not None else None
        self.decoded = DecodedItem(data["decoded"]) if "decoded" in data and data["decoded"] is not None else None

class DecodedItem:
    name: Optional[str]
    signature: Optional[str]
    params: Optional[List["Param"]]

    def __init__(self, data):
        self.name = data["name"] if "name" in data and data["name"] is not None else None
        self.signature = data["signature"] if "signature" in data and data["signature"] is not None else None
        self.params = [Param(item_data) for item_data in data["params"]] if "params" in data and data["params"] is not None else None

class Param:
    name: Optional[str]
    type: Optional[str]
    indexed: Optional[bool]
    decoded: Optional[bool]
    value: Optional[str]

    def __init__(self, data):
        self.name = data["name"] if "name" in data and data["name"] is not None else None
        self.type = data["type"] if "type" in data and data["type"] is not None else None
        self.indexed = data["indexed"] if "indexed" in data and data["indexed"] is not None else None
        self.decoded = data["decoded"] if "decoded" in data and data["decoded"] is not None else None
        self.value = data["value"] if "value" in data and data["value"] is not None else None
            

class NftCollectionTraitsResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    items: List["NftTrait"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.items = [NftTrait(item_data) for item_data in data["items"]]

class NftTrait:
    name: Optional[str]

    def __init__(self, data):
        self.name = data["name"] if "name" in data and data["name"] is not None else None
            

class NftCollectionAttributesForTraitResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    items: List["NftSummaryAttribute"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.items = [NftSummaryAttribute(item_data) for item_data in data["items"]]

class NftSummaryAttribute:
    trait_type: Optional[str]
    values: Optional[List["NftAttribute"]]
    unique_values: Optional[int]

    def __init__(self, data):
        self.trait_type = data["trait_type"] if "trait_type" in data and data["trait_type"] is not None else None
        self.unique_values = int(data["unique_values"]) if "unique_values" in data and data["unique_values"] is not None else None
        self.values = [NftAttribute(item_data) for item_data in data["values"]] if "values" in data and data["values"] is not None else None

class NftAttribute:
    value: Optional[str]
    count: Optional[int]

    def __init__(self, data):
        self.value = data["value"] if "value" in data and data["value"] is not None else None
        self.count = int(data["count"]) if "count" in data and data["count"] is not None else None
            

class NftCollectionTraitSummaryResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    items: List["NftTraitSummary"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.items = [NftTraitSummary(item_data) for item_data in data["items"]]

class NftTraitSummary:
    name: Optional[str]
    """ Trait name """
    value_type: Optional[str]
    """ Type of the value of the trait. """
    value_numeric: Optional["NftTraitNumeric"]
    """ Populated for `numeric` traits. """
    value_string: Optional["NftTraitString"]
    """ Populated for `string` traits. """
    attributes: Optional[List["NftSummaryAttribute"]]

    def __init__(self, data):
        self.name = data["name"] if "name" in data and data["name"] is not None else None
        self.value_type = data["value_type"] if "value_type" in data and data["value_type"] is not None else None
        self.value_numeric = NftTraitNumeric(data["value_numeric"]) if "value_numeric" in data and data["value_numeric"] is not None else None
        self.value_string = NftTraitString(data["value_string"]) if "value_string" in data and data["value_string"] is not None else None
        self.attributes = [NftSummaryAttribute(item_data) for item_data in data["attributes"]] if "attributes" in data and data["attributes"] is not None else None

class NftTraitNumeric:
    min: Optional[float]
    max: Optional[float]

    def __init__(self, data):
        self.min = data["min"] if "min" in data and data["min"] is not None else None
        self.max = data["max"] if "max" in data and data["max"] is not None else None
            

class NftTraitString:
    value: Optional[str]
    """ String value """
    token_count: Optional[int]
    """ Number of distinct tokens that have this trait value. """
    trait_percentage: Optional[float]
    """ Percentage of tokens in the collection that have this trait. """

    def __init__(self, data):
        self.value = data["value"] if "value" in data and data["value"] is not None else None
        self.token_count = int(data["token_count"]) if "token_count" in data and data["token_count"] is not None else None
        self.trait_percentage = data["trait_percentage"] if "trait_percentage" in data and data["trait_percentage"] is not None else None
            

class NftOwnershipForCollectionResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    address: str
    """ The requested address. """
    collection: str
    """ The requested collection. """
    is_spam: bool
    """ Denotes whether the token is suspected spam. Supports `eth-mainnet` and `matic-mainnet`. """
    items: List["NftOwnershipForCollectionItem"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.address = data["address"]
        self.collection = data["collection"]
        self.is_spam = data["is_spam"]
        self.items = [NftOwnershipForCollectionItem(item_data) for item_data in data["items"]]

class NftOwnershipForCollectionItem:
    contract_name: Optional[str]
    """ The string returned by the `name()` method. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    token_id: Optional[int]
    """ The token's id. """
    supports_erc: Optional[List[str]]
    """ A list of supported standard ERC interfaces, eg: `ERC20` and `ERC721`. """
    last_transfered_at: Optional[datetime]
    balance: Optional[int]
    """ Nft balance. """
    balance_24h: Optional[int]
    type: Optional[str]
    nft_data: Optional["NftData"]

    def __init__(self, data):
        self.contract_name = data["contract_name"] if "contract_name" in data and data["contract_name"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.token_id = int(data["token_id"]) if "token_id" in data and data["token_id"] is not None else None
        self.supports_erc = data["supports_erc"] if "supports_erc" in data and data["supports_erc"] is not None else None
        self.last_transfered_at = datetime.fromisoformat(data["last_transfered_at"]) if "last_transfered_at" in data and data["last_transfered_at"] is not None else None
        self.balance = int(data["balance"]) if "balance" in data and data["balance"] is not None else None
        self.balance_24h = int(data["balance_24h"]) if "balance_24h" in data and data["balance_24h"] is not None else None
        self.type = data["type"] if "type" in data and data["type"] is not None else None
        self.nft_data = NftData(data["nft_data"]) if "nft_data" in data and data["nft_data"] is not None else None
    
class NftMarketSaleCountResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    address: str
    """ The requested address. """
    quote_currency: str
    """ The requested quote currency eg: `USD`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    items: List["MarketSaleCountItem"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.address = data["address"]
        self.quote_currency = data["quote_currency"]
        self.chain_name = data["chain_name"]
        self.chain_id = int(data["chain_id"])
        self.items = [MarketSaleCountItem(item_data) for item_data in data["items"]]

class MarketSaleCountItem:
    date: Optional[datetime]
    """ The timestamp of the date of sale. """
    sale_count: Optional[int]
    """ The total amount of sales for the current day. """

    def __init__(self, data):
        self.date = datetime.fromisoformat(data["date"]) if "date" in data and data["date"] is not None else None
        self.sale_count = int(data["sale_count"]) if "sale_count" in data and data["sale_count"] is not None else None
            

class NftMarketVolumeResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    address: str
    """ The requested address. """
    quote_currency: str
    """ The requested quote currency eg: `USD`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    items: List["MarketVolumeItem"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.address = data["address"]
        self.quote_currency = data["quote_currency"]
        self.chain_name = data["chain_name"]
        self.chain_id = int(data["chain_id"])
        self.items = [MarketVolumeItem(item_data) for item_data in data["items"]]

class MarketVolumeItem:
    date: Optional[datetime]
    """ The timestamp of the date of sale. """
    native_ticker_symbol: Optional[str]
    """ The ticker symbol for the native currency. """
    native_name: Optional[str]
    """ The contract name of the native currency. """
    volume_quote: Optional[float]
    """ The current volume converted to fiat in `quote-currency`. """
    volume_native_quote: Optional[float]
    """ The current volume in native currency. """
    pretty_volume_quote: Optional[str]
    """ A prettier version of the volume quote for rendering purposes. """

    def __init__(self, data):
        self.date = datetime.fromisoformat(data["date"]) if "date" in data and data["date"] is not None else None
        self.native_ticker_symbol = data["native_ticker_symbol"] if "native_ticker_symbol" in data and data["native_ticker_symbol"] is not None else None
        self.native_name = data["native_name"] if "native_name" in data and data["native_name"] is not None else None
        self.volume_quote = data["volume_quote"] if "volume_quote" in data and data["volume_quote"] is not None else None
        self.volume_native_quote = data["volume_native_quote"] if "volume_native_quote" in data and data["volume_native_quote"] is not None else None
        self.pretty_volume_quote = data["pretty_volume_quote"] if "pretty_volume_quote" in data and data["pretty_volume_quote"] is not None else None
            

class NftMarketFloorPriceResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    address: str
    """ The requested address. """
    quote_currency: str
    """ The requested quote currency eg: `USD`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    items: List["MarketFloorPriceItem"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.address = data["address"]
        self.quote_currency = data["quote_currency"]
        self.chain_name = data["chain_name"]
        self.chain_id = int(data["chain_id"])
        self.items = [MarketFloorPriceItem(item_data) for item_data in data["items"]]

class MarketFloorPriceItem:
    date: Optional[datetime]
    """ The timestamp of the date of sale. """
    native_ticker_symbol: Optional[str]
    """ The ticker symbol for the native currency. """
    native_name: Optional[str]
    """ The contract name of the native currency. """
    floor_price_native_quote: Optional[float]
    """ The current floor price in native currency. """
    floor_price_quote: Optional[float]
    """ The current floor price converted to fiat in `quote-currency`. """
    pretty_floor_price_quote: Optional[str]
    """ A prettier version of the floor price quote for rendering purposes. """

    def __init__(self, data):
        self.date = datetime.fromisoformat(data["date"]) if "date" in data and data["date"] is not None else None
        self.native_ticker_symbol = data["native_ticker_symbol"] if "native_ticker_symbol" in data and data["native_ticker_symbol"] is not None else None
        self.native_name = data["native_name"] if "native_name" in data and data["native_name"] is not None else None
        self.floor_price_native_quote = data["floor_price_native_quote"] if "floor_price_native_quote" in data and data["floor_price_native_quote"] is not None else None
        self.floor_price_quote = data["floor_price_quote"] if "floor_price_quote" in data and data["floor_price_quote"] is not None else None
        self.pretty_floor_price_quote = data["pretty_floor_price_quote"] if "pretty_floor_price_quote" in data and data["pretty_floor_price_quote"] is not None else None


class NftService:
    __api_key: str
    __debug: Optional[bool]
    def __init__(self, api_key: str, debug: Optional[bool] = False):
        self.__api_key = api_key
        self.__debug = debug


    async def get_chain_collections(self, chain_name: chain, page_size: Optional[int] = None, page_number: Optional[int] = None, no_spam: Optional[bool] = None) -> AsyncIterable[ChainCollectionItem]:
        """
        Commonly used to fetch the list of NFT collections with downloaded and cached off chain data like token metadata and asset files.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        page_size (int): Number of items per page. Omitting this parameter defaults to 100.
        page_number (int): 0-indexed page number to begin pagination.
        no_spam (bool): If `true`, the suspected spam tokens are removed. Supports `eth-mainnet` and `matic-mainnet`.
        """
        success = False
        response = None
        while not success:
            try:
                url_params = {}
                
                if page_size is not None:
                    url_params["page-size"] = str(page_size)
                
                if page_number is not None:
                    url_params["page-number"] = str(page_number)
                
                if no_spam is not None:
                    url_params["no-spam"] = str(no_spam)
                

                async for response in paginate_endpoint(f"https://api.covalenthq.com/v1/{chain_name}/nft/collections/", self.__api_key, url_params, ChainCollectionItem, self.__debug):
                    yield response

                success = True
            except Exception as error:
                success = True
                raise Exception(error)
    
    def get_chain_collections_by_page(self, chain_name: chain, page_size: Optional[int] = None, page_number: Optional[int] = None, no_spam: Optional[bool] = None) -> Response[ChainCollectionResponse]:
        """
        Commonly used to fetch the list of NFT collections with downloaded and cached off chain data like token metadata and asset files.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        page_size (int): Number of items per page. Omitting this parameter defaults to 100.
        page_number (int): 0-indexed page number to begin pagination.
        no_spam (bool): If `true`, the suspected spam tokens are removed. Supports `eth-mainnet` and `matic-mainnet`.
        """
        success = False
        data: Optional[Response[ChainCollectionResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if page_size is not None:
                    url_params["page-size"] = str(page_size)
                
                if page_number is not None:
                    url_params["page-number"] = str(page_number)
                
                if no_spam is not None:
                    url_params["no-spam"] = str(no_spam)
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/nft/collections/", params=url_params, headers={
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

                data_class = ChainCollectionResponse(data.data)
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
        
    def get_nfts_for_address(self, chain_name: chain, wallet_address: str, no_spam: Optional[bool] = None, no_nft_asset_metadata: Optional[bool] = None, with_uncached: Optional[bool] = None) -> Response[NftAddressBalanceNftResponse]:
        """
        Commonly used to render the NFTs (including ERC721 and ERC1155) held by an address.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        no_spam (bool): If `true`, the suspected spam tokens are removed. Supports `eth-mainnet` and `matic-mainnet`.
        no_nft_asset_metadata (bool): If `true`, the response shape is limited to a list of collections and token ids, omitting metadata and asset information. Helpful for faster response times and wallets holding a large number of NFTs.
        with_uncached (bool): By default, this endpoint only works on chains where we've cached the assets and the metadata. When set to `true`, the API will fetch metadata from upstream servers even if it's not cached - the downside being that the upstream server can block or rate limit the call and therefore resulting in time outs or slow response times on the Covalent side.
        """
        success = False
        data: Optional[Response[NftAddressBalanceNftResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if no_spam is not None:
                    url_params["no-spam"] = str(no_spam)
                    
                if no_nft_asset_metadata is not None:
                    url_params["no-nft-asset-metadata"] = str(no_nft_asset_metadata)
                    
                if with_uncached is not None:
                    url_params["with-uncached"] = str(with_uncached)
                    

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/balances_nft/", params=url_params, headers={
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

                data_class = NftAddressBalanceNftResponse(data.data)
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
        
    async def get_token_ids_for_contract_with_metadata(self, chain_name: chain, contract_address: str, no_metadata: Optional[bool] = None, page_size: Optional[int] = None, page_number: Optional[int] = None, traits_filter: Optional[str] = None, values_filter: Optional[str] = None, with_uncached: Optional[bool] = None) -> AsyncIterable[NftTokenContract]:
        """
        Commonly used to get NFT token IDs with metadata from a collection. Useful for building NFT card displays.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        contract_address (str): The requested contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        no_metadata (bool): Omit metadata.
        page_size (int): Number of items per page. Omitting this parameter defaults to 100.
        page_number (int): 0-indexed page number to begin pagination.
        traits_filter (str): Filters NFTs based on a specific trait. If this filter is used, the API will return all NFTs with the specified trait. Accepts comma-separated values, is case-sensitive, and requires proper URL encoding.
        values_filter (str): Filters NFTs based on a specific trait value. If this filter is used, the API will return all NFTs with the specified trait value. If used with "traits-filter", only NFTs matching both filters will be returned. Accepts comma-separated values, is case-sensitive, and requires proper URL encoding.
        with_uncached (bool): By default, this endpoint only works on chains where we've cached the assets and the metadata. When set to `true`, the API will fetch metadata from upstream servers even if it's not cached - the downside being that the upstream server can block or rate limit the call and therefore resulting in time outs or slow response times on the Covalent side.
        """
        success = False
        response = None
        while not success:
            try:
                url_params = {}
                
                if no_metadata is not None:
                    url_params["no-metadata"] = str(no_metadata)
                
                if page_size is not None:
                    url_params["page-size"] = str(page_size)
                
                if page_number is not None:
                    url_params["page-number"] = str(page_number)
                
                if traits_filter is not None:
                    url_params["traits-filter"] = str(traits_filter)
                
                if values_filter is not None:
                    url_params["values-filter"] = str(values_filter)
                
                if with_uncached is not None:
                    url_params["with-uncached"] = str(with_uncached)
                

                async for response in paginate_endpoint(f"https://api.covalenthq.com/v1/{chain_name}/nft/{contract_address}/metadata/", self.__api_key, url_params, NftTokenContract, self.__debug):
                    yield response

                success = True
            except Exception as error:
                success = True
                raise Exception(error)
    
    def get_token_ids_for_contract_with_metadata_by_page(self, chain_name: chain, contract_address: str, no_metadata: Optional[bool] = None, page_size: Optional[int] = None, page_number: Optional[int] = None, traits_filter: Optional[str] = None, values_filter: Optional[str] = None, with_uncached: Optional[bool] = None) -> Response[NftMetadataResponse]:
        """
        Commonly used to get NFT token IDs with metadata from a collection. Useful for building NFT card displays.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        contract_address (str): The requested contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        no_metadata (bool): Omit metadata.
        page_size (int): Number of items per page. Omitting this parameter defaults to 100.
        page_number (int): 0-indexed page number to begin pagination.
        traits_filter (str): Filters NFTs based on a specific trait. If this filter is used, the API will return all NFTs with the specified trait. Accepts comma-separated values, is case-sensitive, and requires proper URL encoding.
        values_filter (str): Filters NFTs based on a specific trait value. If this filter is used, the API will return all NFTs with the specified trait value. If used with "traits-filter", only NFTs matching both filters will be returned. Accepts comma-separated values, is case-sensitive, and requires proper URL encoding.
        with_uncached (bool): By default, this endpoint only works on chains where we've cached the assets and the metadata. When set to `true`, the API will fetch metadata from upstream servers even if it's not cached - the downside being that the upstream server can block or rate limit the call and therefore resulting in time outs or slow response times on the Covalent side.
        """
        success = False
        data: Optional[Response[NftMetadataResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if no_metadata is not None:
                    url_params["no-metadata"] = str(no_metadata)
                
                if page_size is not None:
                    url_params["page-size"] = str(page_size)
                
                if page_number is not None:
                    url_params["page-number"] = str(page_number)
                
                if traits_filter is not None:
                    url_params["traits-filter"] = str(traits_filter)
                
                if values_filter is not None:
                    url_params["values-filter"] = str(values_filter)
                
                if with_uncached is not None:
                    url_params["with-uncached"] = str(with_uncached)
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/nft/{contract_address}/metadata/", params=url_params, headers={
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

                data_class = NftMetadataResponse(data.data)
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
        
    def get_nft_metadata_for_given_token_id_for_contract(self, chain_name: chain, contract_address: str, token_id: str, no_metadata: Optional[bool] = None, with_uncached: Optional[bool] = None) -> Response[NftMetadataResponse]:
        """
        Commonly used to get a single NFT metadata by token ID from a collection. Useful for building NFT card displays.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        contract_address (str): The requested contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        no_metadata (bool): Omit metadata.
        with_uncached (bool): By default, this endpoint only works on chains where we've cached the assets and the metadata. When set to `true`, the API will fetch metadata from upstream servers even if it's not cached - the downside being that the upstream server can block or rate limit the call and therefore resulting in time outs or slow response times on the Covalent side.
        token_id (str): The requested token ID.
        """
        success = False
        data: Optional[Response[NftMetadataResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if no_metadata is not None:
                    url_params["no-metadata"] = str(no_metadata)
                    
                if with_uncached is not None:
                    url_params["with-uncached"] = str(with_uncached)

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/nft/{contract_address}/metadata/{token_id}/", params=url_params, headers={
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

                data_class = NftMetadataResponse(data.data)
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
        
    def get_nft_transactions_for_contract_token_id(self, chain_name: chain, contract_address: str, token_id: str, no_spam: Optional[bool] = None) -> Response[NftTransactionsResponse]:
        """
        Commonly used to get all transactions of an NFT token. Useful for building a transaction history table or price chart.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        contract_address (str): The requested contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        token_id (str): The requested token ID.
        no_spam (bool): If `true`, the suspected spam tokens are removed. Supports `eth-mainnet` and `matic-mainnet`.
        """
        success = False
        data: Optional[Response[NftTransactionsResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if no_spam is not None:
                    url_params["no-spam"] = str(no_spam)

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/tokens/{contract_address}/nft_transactions/{token_id}/", params=url_params, headers={
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

                data_class = NftTransactionsResponse(data.data)
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
        
    def get_traits_for_collection(self, chain_name: chain, collection_contract: str) -> Response[NftCollectionTraitsResponse]:
        """
        Commonly used to fetch and render the traits of a collection as seen in rarity calculators.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        collection_contract (str): The requested collection address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        """
        success = False
        data: Optional[Response[NftCollectionTraitsResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/nft/{collection_contract}/traits/", params=url_params, headers={
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

                data_class = NftCollectionTraitsResponse(data.data)
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
        
    def get_attributes_for_trait_in_collection(self, chain_name: chain, collection_contract: str, trait: str) -> Response[NftCollectionAttributesForTraitResponse]:
        """
        Commonly used to get the count of unique values for traits within an NFT collection.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        collection_contract (str): The requested collection address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        trait (str): The requested trait.
        """
        success = False
        data: Optional[Response[NftCollectionAttributesForTraitResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/nft/{collection_contract}/traits/{trait}/attributes/", params=url_params, headers={
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

                data_class = NftCollectionAttributesForTraitResponse(data.data)
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
        
    def get_collection_traits_summary(self, chain_name: chain, collection_contract: str) -> Response[NftCollectionTraitSummaryResponse]:
        """
        Commonly used to calculate rarity scores for a collection based on its traits.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        collection_contract (str): The requested collection address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        """
        success = False
        data: Optional[Response[NftCollectionTraitSummaryResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/nft/{collection_contract}/traits_summary/", params=url_params, headers={
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
                
                data_class = NftCollectionTraitSummaryResponse(data.data)
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
        
    def check_ownership_in_nft(self, chain_name: chain, wallet_address: str, collection_contract: str) -> Response[NftOwnershipForCollectionResponse]:
        """
        Commonly used to verify ownership of NFTs (including ERC-721 and ERC-1155) within a collection.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        collection_contract (str): The requested collection address.
        """
        success = False
        data: Optional[Response[NftOwnershipForCollectionResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/collection/{collection_contract}/", params=url_params, headers={
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

                data_class = NftOwnershipForCollectionResponse(data.data)
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
        
    def check_ownership_in_nft_for_specific_token_id(self, chain_name: chain, wallet_address: str, collection_contract: str, token_id: str) -> Response[NftOwnershipForCollectionResponse]:
        """
        Commonly used to verify ownership of a specific token (ERC-721 or ERC-1155) within a collection.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        collection_contract (str): The requested collection address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        token_id (str): The requested token ID.
        """
        success = False
        data: Optional[Response[NftOwnershipForCollectionResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/collection/{collection_contract}/token/{token_id}/", params=url_params, headers={
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

                data_class = NftOwnershipForCollectionResponse(data.data)
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
    
    def get_nft_market_sale_count(self, chain_name: chain, contract_address: str, days: Optional[int] = None, quote_currency: Optional[quote] = None) -> Response[NftMarketSaleCountResponse]:
        """
        Commonly used to build a time-series chart of the sales count of an NFT collection.
        
        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        contract_address (str): The requested contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        days (int): The number of days to return data for. Request up 365 days. Defaults to 30 days.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        """
        success = False
        data: Optional[Response[NftMarketSaleCountResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if days is not None:
                    url_params["days"] = str(days)
                    
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/nft_market/{contract_address}/sale_count/", params=url_params, headers={
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
                    
                data_class = NftMarketSaleCountResponse(data.data)
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
        
    def get_nft_market_volume(self, chain_name: chain, contract_address: str, days: Optional[int] = None, quote_currency: Optional[quote] = None) -> Response[NftMarketVolumeResponse]:
        """
        Commonly used to build a time-series chart of the transaction volume of an NFT collection.
        
        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        contract_address (str): The requested contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        days (int): The number of days to return data for. Request up 365 days. Defaults to 30 days.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        """
        success = False
        data: Optional[Response[NftMarketVolumeResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if days is not None:
                    url_params["days"] = str(days)
                    
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                    
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/nft_market/{contract_address}/volume/", params=url_params, headers={
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

                data_class = NftMarketVolumeResponse(data.data)
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
        
    def get_nft_market_floor_price(self, chain_name: chain, contract_address: str, days: Optional[int] = None, quote_currency: Optional[quote] = None) -> Response[NftMarketFloorPriceResponse]:
        """
        Commonly used to render a price floor chart for an NFT collection.
        
        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        contract_address (str): The requested contract address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        days (int): The number of days to return data for. Request up 365 days. Defaults to 30 days.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        """
        success = False
        data: Optional[Response[NftMarketFloorPriceResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if days is not None:
                    url_params["days"] = str(days)
                    
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/nft_market/{contract_address}/floor_price/", params=url_params, headers={
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
                    
                data_class = NftMarketFloorPriceResponse(data.data)
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
        
    
    