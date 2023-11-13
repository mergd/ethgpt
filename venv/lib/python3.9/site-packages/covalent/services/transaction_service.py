from datetime import datetime
from typing import AsyncIterable, List, Optional

import requests
from .util.back_off import ExponentialBackoff
from .util.api_helper import check_and_modify_response, paginate_endpoint, Response
from .util.types import chain, quote, user_agent
from .util.debugger import debug_output
import aiohttp

class TransactionResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["Transaction"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [Transaction(item_data) for item_data in data["items"]]

class Transaction:
    block_signed_at: Optional[datetime]
    """ The block signed timestamp in UTC. """
    block_height: Optional[int]
    """ The height of the block. """
    block_hash: Optional[str]
    """ The hash of the block. Use it to remove transactions from re-org-ed blocks. """
    tx_hash: Optional[str]
    """ The requested transaction hash. """
    tx_offset: Optional[int]
    """ The offset is the position of the tx in the block. """
    successful: Optional[bool]
    """ Indicates whether a transaction failed or succeeded. """
    from_address: Optional[str]
    """ The sender's wallet address. """
    miner_address: Optional[str]
    """ The address of the miner. """
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
    gas_metadata: Optional["ContractMetadata"]
    """ The requested chain native gas token metadata. """
    gas_offered: Optional[str]
    gas_spent: Optional[str]
    """ The gas spent for this tx. """
    gas_price: Optional[str]
    """ The gas price at the time of this tx. """
    fees_paid: Optional[int]
    """ The total transaction fees (`gas_price` * `gas_spent`) paid for this tx, denoted in wei. """
    gas_quote: Optional[float]
    """ The gas spent in `quote-currency` denomination. """
    pretty_gas_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """
    gas_quote_rate: Optional[float]
    """ The native gas exchange rate for the requested `quote-currency`. """
    dex_details: Optional["DexReport"]
    """ The details for the dex transaction. """
    nft_sale_details: Optional["NftSalesReport"]
    """ The details for the NFT sale transaction. """
    lending_details: Optional["LendingReport"]
    """ The details for the lending protocol transaction. """
    log_events: Optional[List["LogEvent"]]
    """ The log events. """
    safe_details: Optional[List["SafeDetails"]]
    """ The details related to the safe transaction. """

    def __init__(self, data):
        self.block_signed_at = datetime.fromisoformat(data["block_signed_at"]) if "block_signed_at" in data and data["block_signed_at"] is not None else None
        self.block_height = int(data["block_height"]) if "block_height" in data and data["block_height"] is not None else None
        self.block_hash = data["block_hash"] if "block_hash" in data and data["block_hash"] is not None else None
        self.tx_hash = data["tx_hash"] if "tx_hash" in data and data["tx_hash"] is not None else None
        self.tx_offset = int(data["tx_offset"]) if "tx_offset" in data and data["tx_offset"] is not None else None
        self.successful = data["successful"] if "successful" in data and data["successful"] is not None else None
        self.from_address = data["from_address"] if "from_address" in data and data["from_address"] is not None else None
        self.miner_address = data["miner_address"] if "miner_address" in data and data["miner_address"] is not None else None
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
        self.gas_metadata = ContractMetadata(data["gas_metadata"]) if "gas_metadata" in data and data["gas_metadata"] is not None else None
        self.dex_details = DexReport(data["dex_details"]) if "dex_details" in data and data["dex_details"] is not None else None
        self.nft_sale_details = NftSalesReport(data["nft_sale_details"]) if "nft_sale_details" in data and data["nft_sale_details"] is not None else None
        self.lending_details = LendingReport(data["lending_details"]) if "lending_details" in data and data["lending_details"] is not None else None
        self.log_events = [LogEvent(item_data) for item_data in data["log_events"]] if "log_events" in data and data["log_events"] is not None else None
        self.safe_details = [SafeDetails(item_data) for item_data in data["safe_details"]] if "safe_details" in data and data["safe_details"] is not None else None

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
            

class DexReport:
    log_offset: Optional[int]
    """ The offset is the position of the log entry within an event log. """
    protocol_name: Optional[str]
    """ Stores the name of the protocol that facilitated the event. """
    protocol_address: Optional[str]
    """ Stores the contract address of the protocol that facilitated the event. """
    protocol_logo_url: Optional[str]
    """ Stores the URL of the logo for the protocol that facilitated the event. """
    aggregator_name: Optional[str]
    """ Stores the aggregator responsible for the event. """
    aggregator_address: Optional[str]
    """ Stores the contract address of the aggregator responsible for the event. """
    version: Optional[int]
    """ DEXs often have multiple version - e.g Uniswap V1, V2 and V3. The `version` field allows you to look at a specific version of the DEX. """
    fork_version: Optional[int]
    """ Similarly to the `version` field, `fork_version` gives you the version of the forked DEX. For example, most DEXs are a fork of Uniswap V2; therefore, `fork` = `aave` & `fork_version` = `2` """
    fork: Optional[str]
    """ Many DEXs are a fork of an already established DEX. The fork field allows you to see which DEX has been forked. """
    event: Optional[str]
    """ Stores the event taking place - e.g `swap`, `add_liquidity` and `remove_liquidity`. """
    pair_address: Optional[str]
    """ Stores the address of the pair that the user interacts with. """
    pair_lp_fee_bps: Optional[float]
    lp_token_address: Optional[str]
    lp_token_ticker: Optional[str]
    lp_token_num_decimals: Optional[int]
    lp_token_name: Optional[str]
    lp_token_value: Optional[float]
    exchange_rate_usd: Optional[float]
    token_0_address: Optional[str]
    """ Stores the address of token 0 in the specific pair. """
    token_0_ticker: Optional[str]
    """ Stores the ticker symbol of token 0 in the specific pair. """
    token_0_num_decimals: Optional[int]
    """ Stores the number of contract decimals of token 0 in the specific pair. """
    token_0_name: Optional[str]
    """ Stores the contract name of token 0 in the specific pair. """
    token_1_address: Optional[str]
    """ Stores the address of token 1 in the specific pair. """
    token_1_ticker: Optional[str]
    """ Stores the ticker symbol of token 1 in the specific pair. """
    token_1_num_decimals: Optional[int]
    """ Stores the number of contract decimals of token 1 in the specific pair. """
    token_1_name: Optional[str]
    """ Stores the contract name of token 1 in the specific pair. """
    token_0_amount: Optional[float]
    """ Stores the amount of token 0 used in the transaction. For example, 1 ETH, 100 USDC, 30 UNI, etc. """
    token_0_quote_rate: Optional[float]
    token_0_usd_quote: Optional[float]
    pretty_token_0_usd_quote: Optional[str]
    token_0_logo_url: Optional[str]
    token_1_amount: Optional[float]
    """ Stores the amount of token 1 used in the transaction. For example, 1 ETH, 100 USDC, 30 UNI, etc. """
    token_1_quote_rate: Optional[float]
    token_1_usd_quote: Optional[float]
    pretty_token_1_usd_quote: Optional[str]
    token_1_logo_url: Optional[str]
    sender: Optional[str]
    """ Stores the wallet address that initiated the transaction (i.e the wallet paying the gas fee). """
    recipient: Optional[str]
    """ Stores the recipient of the transaction - recipients can be other wallets or smart contracts. For example, if you want to Swap tokens on Uniswap, the Uniswap router would typically be the recipient of the transaction. """

    def __init__(self, data):
        self.log_offset = int(data["log_offset"]) if "log_offset" in data and data["log_offset"] is not None else None
        self.protocol_name = data["protocol_name"] if "protocol_name" in data and data["protocol_name"] is not None else None
        self.protocol_address = data["protocol_address"] if "protocol_address" in data and data["protocol_address"] is not None else None
        self.protocol_logo_url = data["protocol_logo_url"] if "protocol_logo_url" in data and data["protocol_logo_url"] is not None else None
        self.aggregator_name = data["aggregator_name"] if "aggregator_name" in data and data["aggregator_name"] is not None else None
        self.aggregator_address = data["aggregator_address"] if "aggregator_address" in data and data["aggregator_address"] is not None else None
        self.version = int(data["version"]) if "version" in data and data["version"] is not None else None
        self.fork_version = int(data["fork_version"]) if "fork_version" in data and data["fork_version"] is not None else None
        self.fork = data["fork"] if "fork" in data and data["fork"] is not None else None
        self.event = data["event"] if "event" in data and data["event"] is not None else None
        self.pair_address = data["pair_address"] if "pair_address" in data and data["pair_address"] is not None else None
        self.pair_lp_fee_bps = data["pair_lp_fee_bps"] if "pair_lp_fee_bps" in data and data["pair_lp_fee_bps"] is not None else None
        self.lp_token_address = data["lp_token_address"] if "lp_token_address" in data and data["lp_token_address"] is not None else None
        self.lp_token_ticker = data["lp_token_ticker"] if "lp_token_ticker" in data and data["lp_token_ticker"] is not None else None
        self.lp_token_num_decimals = int(data["lp_token_num_decimals"]) if "lp_token_num_decimals" in data and data["lp_token_num_decimals"] is not None else None
        self.lp_token_name = data["lp_token_name"] if "lp_token_name" in data and data["lp_token_name"] is not None else None
        self.lp_token_value = data["lp_token_value"] if "lp_token_value" in data and data["lp_token_value"] is not None else None
        self.exchange_rate_usd = data["exchange_rate_usd"] if "exchange_rate_usd" in data and data["exchange_rate_usd"] is not None else None
        self.token_0_address = data["token_0_address"] if "token_0_address" in data and data["token_0_address"] is not None else None
        self.token_0_ticker = data["token_0_ticker"] if "token_0_ticker" in data and data["token_0_ticker"] is not None else None
        self.token_0_num_decimals = int(data["token_0_num_decimals"]) if "token_0_num_decimals" in data and data["token_0_num_decimals"] is not None else None
        self.token_0_name = data["token_0_name"] if "token_0_name" in data and data["token_0_name"] is not None else None
        self.token_1_address = data["token_1_address"] if "token_1_address" in data and data["token_1_address"] is not None else None
        self.token_1_ticker = data["token_1_ticker"] if "token_1_ticker" in data and data["token_1_ticker"] is not None else None
        self.token_1_num_decimals = int(data["token_1_num_decimals"]) if "token_1_num_decimals" in data and data["token_1_num_decimals"] is not None else None
        self.token_1_name = data["token_1_name"] if "token_1_name" in data and data["token_1_name"] is not None else None
        self.token_0_amount = data["token_0_amount"] if "token_0_amount" in data and data["token_0_amount"] is not None else None
        self.token_0_quote_rate = data["token_0_quote_rate"] if "token_0_quote_rate" in data and data["token_0_quote_rate"] is not None else None
        self.token_0_usd_quote = data["token_0_usd_quote"] if "token_0_usd_quote" in data and data["token_0_usd_quote"] is not None else None
        self.pretty_token_0_usd_quote = data["pretty_token_0_usd_quote"] if "pretty_token_0_usd_quote" in data and data["pretty_token_0_usd_quote"] is not None else None
        self.token_0_logo_url = data["token_0_logo_url"] if "token_0_logo_url" in data and data["token_0_logo_url"] is not None else None
        self.token_1_amount = data["token_1_amount"] if "token_1_amount" in data and data["token_1_amount"] is not None else None
        self.token_1_quote_rate = data["token_1_quote_rate"] if "token_1_quote_rate" in data and data["token_1_quote_rate"] is not None else None
        self.token_1_usd_quote = data["token_1_usd_quote"] if "token_1_usd_quote" in data and data["token_1_usd_quote"] is not None else None
        self.pretty_token_1_usd_quote = data["pretty_token_1_usd_quote"] if "pretty_token_1_usd_quote" in data and data["pretty_token_1_usd_quote"] is not None else None
        self.token_1_logo_url = data["token_1_logo_url"] if "token_1_logo_url" in data and data["token_1_logo_url"] is not None else None
        self.sender = data["sender"] if "sender" in data and data["sender"] is not None else None
        self.recipient = data["recipient"] if "recipient" in data and data["recipient"] is not None else None
            

class NftSalesReport:
    log_offset: Optional[int]
    """ The offset is the position of the log entry within an event log. """
    topic0: Optional[str]
    """ Stores the topic event hash. All events have a unique topic event hash. """
    protocol_contract_address: Optional[str]
    """ Stores the contract address of the protocol that facilitated the event. """
    protocol_name: Optional[str]
    """ Stores the name of the protocol that facilitated the event. """
    protocol_logo_url: Optional[str]
    """ Stores the URL of the logo for the protocol that facilitated the event. """
    to: Optional[str]
    """ Stores the address of the transaction recipient. """
    _from: Optional[str]
    """ Stores the address of the transaction sender. """
    maker: Optional[str]
    """ Stores the address selling the NFT. """
    taker: Optional[str]
    """ Stores the address buying the NFT. """
    token_id: Optional[float]
    """ Stores the NFTs token ID. All NFTs have a token ID. Within a collection, these token IDs are unique. If the NFT is transferred to another owner, the token id remains the same, as this number is its identifier within a collection. For example, if a collection has 10K NFTs then an NFT in that collection can have a token ID from 1-10K. """
    collection_address: Optional[str]
    """ Stores the address of the collection. For example, [Bored Ape Yacht Club](https://etherscan.io/token/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d) """
    collection_name: Optional[str]
    """ Stores the name of the collection. """
    token_address: Optional[str]
    """ Stores the address of the token used to purchase the NFT. """
    token_name: Optional[str]
    """ Stores the name of the token used to purchase the NFT. """
    ticker_symbol: Optional[str]
    """ Stores the ticker symbol of the token used to purchase the NFT. """
    num_decimals: Optional[int]
    """ Stores the number decimal of the token used to purchase the NFT. """
    contract_quote_rate: Optional[float]
    nft_token_price: Optional[float]
    """ The token amount used to purchase the NFT. For example, if the user purchased an NFT for 1 ETH. The `nft_token_price` field will hold `1`. """
    nft_token_price_usd: Optional[float]
    """ The USD amount used to purchase the NFT. """
    pretty_nft_token_price_usd: Optional[str]
    nft_token_price_native: Optional[float]
    """ The price of the NFT denominated in the chains native token. Even if a seller sells their NFT for DAI or MANA, this field denominates the price in the native token (e.g. ETH, AVAX, FTM, etc.) """
    pretty_nft_token_price_native: Optional[str]
    token_count: Optional[int]
    """ Stores the number of NFTs involved in the sale. It's quick routine to see multiple NFTs involved in a single sale. """
    num_token_ids_sold_per_sale: Optional[int]
    num_token_ids_sold_per_tx: Optional[int]
    num_collections_sold_per_sale: Optional[int]
    num_collections_sold_per_tx: Optional[int]
    trade_type: Optional[str]
    trade_group_type: Optional[str]

    def __init__(self, data):
        self.log_offset = int(data["log_offset"]) if "log_offset" in data and data["log_offset"] is not None else None
        self.topic0 = data["topic0"] if "topic0" in data and data["topic0"] is not None else None
        self.protocol_contract_address = data["protocol_contract_address"] if "protocol_contract_address" in data and data["protocol_contract_address"] is not None else None
        self.protocol_name = data["protocol_name"] if "protocol_name" in data and data["protocol_name"] is not None else None
        self.protocol_logo_url = data["protocol_logo_url"] if "protocol_logo_url" in data and data["protocol_logo_url"] is not None else None
        self.to = data["to"] if "to" in data and data["to"] is not None else None
        self._from = data["from"] if "from" in data and data["from"] is not None else None
        self.maker = data["maker"] if "maker" in data and data["maker"] is not None else None
        self.taker = data["taker"] if "taker" in data and data["taker"] is not None else None
        self.token_id = data["token_id"] if "token_id" in data and data["token_id"] is not None else None
        self.collection_address = data["collection_address"] if "collection_address" in data and data["collection_address"] is not None else None
        self.collection_name = data["collection_name"] if "collection_name" in data and data["collection_name"] is not None else None
        self.token_address = data["token_address"] if "token_address" in data and data["token_address"] is not None else None
        self.token_name = data["token_name"] if "token_name" in data and data["token_name"] is not None else None
        self.ticker_symbol = data["ticker_symbol"] if "ticker_symbol" in data and data["ticker_symbol"] is not None else None
        self.num_decimals = int(data["num_decimals"]) if "num_decimals" in data and data["num_decimals"] is not None else None
        self.contract_quote_rate = data["contract_quote_rate"] if "contract_quote_rate" in data and data["contract_quote_rate"] is not None else None
        self.nft_token_price = data["nft_token_price"] if "nft_token_price" in data and data["nft_token_price"] is not None else None
        self.nft_token_price_usd = data["nft_token_price_usd"] if "nft_token_price_usd" in data and data["nft_token_price_usd"] is not None else None
        self.pretty_nft_token_price_usd = data["pretty_nft_token_price_usd"] if "pretty_nft_token_price_usd" in data and data["pretty_nft_token_price_usd"] is not None else None
        self.nft_token_price_native = data["nft_token_price_native"] if "nft_token_price_native" in data and data["nft_token_price_native"] is not None else None
        self.pretty_nft_token_price_native = data["pretty_nft_token_price_native"] if "pretty_nft_token_price_native" in data and data["pretty_nft_token_price_native"] is not None else None
        self.token_count = int(data["token_count"]) if "token_count" in data and data["token_count"] is not None else None
        self.num_token_ids_sold_per_sale = int(data["num_token_ids_sold_per_sale"]) if "num_token_ids_sold_per_sale" in data and data["num_token_ids_sold_per_sale"] is not None else None
        self.num_token_ids_sold_per_tx = int(data["num_token_ids_sold_per_tx"]) if "num_token_ids_sold_per_tx" in data and data["num_token_ids_sold_per_tx"] is not None else None
        self.num_collections_sold_per_sale = int(data["num_collections_sold_per_sale"]) if "num_collections_sold_per_sale" in data and data["num_collections_sold_per_sale"] is not None else None
        self.num_collections_sold_per_tx = int(data["num_collections_sold_per_tx"]) if "num_collections_sold_per_tx" in data and data["num_collections_sold_per_tx"] is not None else None
        self.trade_type = data["trade_type"] if "trade_type" in data and data["trade_type"] is not None else None
        self.trade_group_type = data["trade_group_type"] if "trade_group_type" in data and data["trade_group_type"] is not None else None
  

class LendingReport:
    log_offset: Optional[int]
    """ The offset is the position of the log entry within an event log. """
    protocol_name: Optional[str]
    """ Stores the name of the lending protocol that facilitated the event. """
    protocol_address: Optional[str]
    """ Stores the contract address of the lending protocol that facilitated the event. """
    protocol_logo_url: Optional[str]
    """ Stores the logo URL of the lending protocol that facilitated the event. """
    version: Optional[str]
    """ Lending protocols often have multiple version (e.g. Aave V1, V2 and V3). The `version` field allows you to look at a specific version of the Lending protocol. """
    fork: Optional[str]
    """ Many lending protocols are a fork of an already established protocol. The fork column allows you to see which lending protocol has been forked. """
    fork_version: Optional[str]
    """ Similarly to the `version` column, `fork_version` gives you the version of the forked lending protocol. For example, most lending protocols in the space are a fork of Aave V2; therefore, `fork` = `aave` & `fork_version` = `2` """
    event: Optional[str]
    """ Stores the event taking place - e.g `borrow`, `deposit`, `liquidation`, 'repay' and 'withdraw'. """
    lp_token_name: Optional[str]
    """ Stores the name of the LP token issued by the lending protocol. LP tokens can be debt or interest bearing tokens. """
    lp_decimals: Optional[int]
    """ Stores the number decimal of the LP token. """
    lp_ticker_symbol: Optional[str]
    """ Stores the ticker symbol of the LP token. """
    lp_token_address: Optional[str]
    """ Stores the token address of the LP token. """
    lp_token_amount: Optional[float]
    """ Stores the amount of LP token used in the event (e.g. 1 aETH, 100 cUSDC, etc). """
    lp_token_price: Optional[float]
    """ Stores the total USD amount of all the LP Token used in the event. """
    exchange_rate: Optional[float]
    """ Stores the exchange rate between the LP and underlying token. """
    exchange_rate_usd: Optional[float]
    """ Stores the USD price of the LP Token used in the event. """
    token_name_in: Optional[str]
    """ Stores the name of the token going into the lending protocol (e.g the token getting deposited). """
    token_decimal_in: Optional[int]
    """ Stores the number decimal of the token going into the lending protocol. """
    token_address_in: Optional[str]
    """ Stores the address of the token going into the lending protocol. """
    token_ticker_in: Optional[str]
    """ Stores the ticker symbol of the token going into the lending protocol. """
    token_logo_in: Optional[str]
    """ Stores the logo URL of the token going into the lending protocol. """
    token_amount_in: Optional[float]
    """ Stores the amount of tokens going into the lending protocol (e.g 1 ETH, 100 USDC, etc). """
    amount_in_usd: Optional[float]
    """ Stores the total USD amount of all tokens going into the lending protocol. """
    pretty_amount_in_usd: Optional[str]
    token_name_out: Optional[str]
    """ Stores the name of the token going out of the lending protocol (e.g the token getting deposited). """
    token_decimals_out: Optional[int]
    """ Stores the number decimal of the token going out of the lending protocol. """
    token_address_out: Optional[str]
    """ Stores the address of the token going out of the lending protocol. """
    token_ticker_out: Optional[str]
    """ Stores the ticker symbol of the token going out of the lending protocol. """
    token_logo_out: Optional[str]
    """ Stores the logo URL of the token going out of the lending protocol. """
    token_amount_out: Optional[float]
    """ Stores the amount of tokens going out of the lending protocol (e.g 1 ETH, 100 USDC, etc). """
    amount_out_usd: Optional[float]
    """ Stores the total USD amount of all tokens going out of the lending protocol. """
    pretty_amount_out_usd: Optional[str]
    borrow_rate_mode: Optional[float]
    """ Stores the type of loan the user is taking out. Lending protocols enable you to take out a stable or variable loan. Only relevant to borrow events. """
    borrow_rate: Optional[float]
    """ Stores the interest rate of the loan. Only relevant to borrow events. """
    on_behalf_of: Optional[str]
    liquidator: Optional[str]
    """ Stores the wallet address liquidating the loan. Only relevant to liquidation events. """
    user: Optional[str]
    """ Stores the wallet address of the user initiating the event. """

    def __init__(self, data):
        self.log_offset = int(data["log_offset"]) if "log_offset" in data and data["log_offset"] is not None else None
        self.protocol_name = data["protocol_name"] if "protocol_name" in data and data["protocol_name"] is not None else None
        self.protocol_address = data["protocol_address"] if "protocol_address" in data and data["protocol_address"] is not None else None
        self.protocol_logo_url = data["protocol_logo_url"] if "protocol_logo_url" in data and data["protocol_logo_url"] is not None else None
        self.version = data["version"] if "version" in data and data["version"] is not None else None
        self.fork = data["fork"] if "fork" in data and data["fork"] is not None else None
        self.fork_version = data["fork_version"] if "fork_version" in data and data["fork_version"] is not None else None
        self.event = data["event"] if "event" in data and data["event"] is not None else None
        self.lp_token_name = data["lp_token_name"] if "lp_token_name" in data and data["lp_token_name"] is not None else None
        self.lp_decimals = int(data["lp_decimals"]) if "lp_decimals" in data and data["lp_decimals"] is not None else None
        self.lp_ticker_symbol = data["lp_ticker_symbol"] if "lp_ticker_symbol" in data and data["lp_ticker_symbol"] is not None else None
        self.lp_token_address = data["lp_token_address"] if "lp_token_address" in data and data["lp_token_address"] is not None else None
        self.lp_token_amount = data["lp_token_amount"] if "lp_token_amount" in data and data["lp_token_amount"] is not None else None
        self.lp_token_price = data["lp_token_price"] if "lp_token_price" in data and data["lp_token_price"] is not None else None
        self.exchange_rate = data["exchange_rate"] if "exchange_rate" in data and data["exchange_rate"] is not None else None
        self.exchange_rate_usd = data["exchange_rate_usd"] if "exchange_rate_usd" in data and data["exchange_rate_usd"] is not None else None
        self.token_name_in = data["token_name_in"] if "token_name_in" in data and data["token_name_in"] is not None else None
        self.token_decimal_in = int(data["token_decimal_in"]) if "token_decimal_in" in data and data["token_decimal_in"] is not None else None
        self.token_address_in = data["token_address_in"] if "token_address_in" in data and data["token_address_in"] is not None else None
        self.token_ticker_in = data["token_ticker_in"] if "token_ticker_in" in data and data["token_ticker_in"] is not None else None
        self.token_logo_in = data["token_logo_in"] if "token_logo_in" in data and data["token_logo_in"] is not None else None
        self.token_amount_in = data["token_amount_in"] if "token_amount_in" in data and data["token_amount_in"] is not None else None
        self.amount_in_usd = data["amount_in_usd"] if "amount_in_usd" in data and data["amount_in_usd"] is not None else None
        self.pretty_amount_in_usd = data["pretty_amount_in_usd"] if "pretty_amount_in_usd" in data and data["pretty_amount_in_usd"] is not None else None
        self.token_name_out = data["token_name_out"] if "token_name_out" in data and data["token_name_out"] is not None else None
        self.token_decimals_out = int(data["token_decimals_out"]) if "token_decimals_out" in data and data["token_decimals_out"] is not None else None
        self.token_address_out = data["token_address_out"] if "token_address_out" in data and data["token_address_out"] is not None else None
        self.token_ticker_out = data["token_ticker_out"] if "token_ticker_out" in data and data["token_ticker_out"] is not None else None
        self.token_logo_out = data["token_logo_out"] if "token_logo_out" in data and data["token_logo_out"] is not None else None
        self.token_amount_out = data["token_amount_out"] if "token_amount_out" in data and data["token_amount_out"] is not None else None
        self.amount_out_usd = data["amount_out_usd"] if "amount_out_usd" in data and data["amount_out_usd"] is not None else None
        self.pretty_amount_out_usd = data["pretty_amount_out_usd"] if "pretty_amount_out_usd" in data and data["pretty_amount_out_usd"] is not None else None
        self.borrow_rate_mode = data["borrow_rate_mode"] if "borrow_rate_mode" in data and data["borrow_rate_mode"] is not None else None
        self.borrow_rate = data["borrow_rate"] if "borrow_rate" in data and data["borrow_rate"] is not None else None
        self.on_behalf_of = data["on_behalf_of"] if "on_behalf_of" in data and data["on_behalf_of"] is not None else None
        self.liquidator = data["liquidator"] if "liquidator" in data and data["liquidator"] is not None else None
        self.user = data["user"] if "user" in data and data["user"] is not None else None
            

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

class SafeDetails:
    owner_address: Optional[str]
    """ The address that signed the safe transaction. """
    signature: Optional[str]
    """ The signature of the owner for the safe transaction. """
    signature_type: Optional[str]
    """ The type of safe signature used. """

    def __init__(self, data):
        self.owner_address = data["owner_address"] if "owner_address" in data and data["owner_address"] is not None else None
        self.signature = data["signature"] if "signature" in data and data["signature"] is not None else None
        self.signature_type = data["signature_type"] if "signature_type" in data and data["signature_type"] is not None else None
            

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
     

class RecentTransactionsResponse:
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
    current_page: int
    """ The current page of the response. """
    links: "PaginationLinks"
    items: List["Transaction"]
    """ List of response items. """

    def __init__(self, data):
        self.address = data["address"]
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.quote_currency = data["quote_currency"]
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.current_page = int(data["current_page"])
        self.links = PaginationLinks(data["links"])
        self.items = [Transaction(item_data) for item_data in data["items"]]

class PaginationLinks:
    prev: Optional[str]
    """ URL link to the next page. """
    next: Optional[str]
    """ URL link to the previous page. """

    def __init__(self, data):
        self.prev = data["prev"] if "prev" in data and data["prev"] is not None else None
        self.next = data["next"] if "next" in data and data["next"] is not None else None


class TransactionsBlockResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["Transaction"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [Transaction(item_data) for item_data in data["items"]]

class TransactionsSummaryResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    address: str
    """ The requested address. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    items: List["TransactionsSummary"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.address = data["address"]
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [TransactionsSummary(item_data) for item_data in data["items"]]

class TransactionsSummary:
    total_count: Optional[int]
    """ The total number of transactions. """
    earliest_transaction: Optional["TransactionSummary"]
    """ The earliest transaction detected. """
    latest_transaction: Optional["TransactionSummary"]
    """ The latest transaction detected. """

    def __init__(self, data):
        self.total_count = int(data["total_count"]) if "total_count" in data and data["total_count"] is not None else None
        self.earliest_transaction = TransactionSummary(data["earliest_transaction"]) if "earliest_transaction" in data and data["earliest_transaction"] is not None else None
        self.latest_transaction = TransactionSummary(data["latest_transaction"]) if "latest_transaction" in data and data["latest_transaction"] is not None else None

class TransactionSummary:
    block_signed_at: Optional[datetime]
    """ The block signed timestamp in UTC. """
    tx_hash: Optional[str]
    """ The requested transaction hash. """
    tx_detail_link: Optional[str]
    """ The link to the transaction details using the Covalent API. """

    def __init__(self, data):
        self.block_signed_at = datetime.fromisoformat(data["block_signed_at"]) if "block_signed_at" in data and data["block_signed_at"] is not None else None
        self.tx_hash = data["tx_hash"] if "tx_hash" in data and data["tx_hash"] is not None else None
        self.tx_detail_link = data["tx_detail_link"] if "tx_detail_link" in data and data["tx_detail_link"] is not None else None

class TransactionsResponse:
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
    current_page: int
    """ The current page of the response. """
    links: "PaginationLinks"
    items: List["Transaction"]
    """ List of response items. """

    def __init__(self, data):
        self.address = data["address"]
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.quote_currency = data["quote_currency"]
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.current_page = int(data["current_page"])
        self.links = PaginationLinks(data["links"])
        self.items = [Transaction(item_data) for item_data in data["items"]]

async def paginate_endpoint(url: str, api_key: str, urls_params, debug: Optional[bool] = False) -> AsyncIterable[Transaction]:
    has_next = True
    backoff = ExponentialBackoff(api_key, debug)
    data = None
    while has_next:
        try:
            
            start_time = None
            if debug:
                start_time = datetime.now()

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}", params=urls_params, headers={"Authorization": f"Bearer {api_key}", "X-Requested-With": user_agent}) as response:
                    
                    debug_output(response.url, response.status, start_time)
        
                    if response.status == 429:
                        try:
                            data = backoff.back_off(response.url)
                        except Exception as e:
                            has_next = False
                            raise Exception(f"An error occurred {response.status}: {e}")
                    else:
                        data = await response.json()
                    
                    for tx in data.get("data").get("items"):
                        data_class = Transaction(tx)
                        check_and_modify_response(data_class)
                        yield data_class
                    
                    backoff.set_num_attempts(1)

                    if not data.get("error"):
                        if data.get("data") is not None and data.get("data").get("links").get("prev") is None:
                            has_next = False
                        url = data.get("data").get("links").get("prev") if data.get("data") is not None and data.get("data").get("links").get("prev") is not None else ""
                    else:
                        has_next = False
        except Exception as e:
            has_next = False
            error_message = str(e)  # Get the error message as a string
            if "An error occurred 429" in error_message:
                raise Exception(error_message)
            raise Exception(f"An error occurred {data.get('error_code') if data else response.status}: {data.get('error_message') if data else 'Internal server error' if response.status == 500 else '401 Authorization Required'}")



            
class TransactionService:
    __api_key: str
    __debug: Optional[bool]
    def __init__(self, api_key: str, debug: Optional[bool] = False):
        self.__api_key = api_key
        self.__debug = debug


    def get_transaction(self, chain_name: chain, tx_hash: str, quote_currency: Optional[quote] = None, no_logs: Optional[bool] = None, with_dex: Optional[bool] = None, with_nft_sales: Optional[bool] = None, with_lending: Optional[bool] = None, with_safe: Optional[bool] = None) -> Response[TransactionResponse]:
        """
        Commonly used to fetch and render a single transaction including its decoded log events. Additionally return semantically decoded information for DEX trades, lending and NFT sales.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        tx_hash (str): The transaction hash.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        no_logs (bool): Omit log events.
        with_dex (bool): Decoded DEX details including protocol (e.g. Uniswap), event (e.g 'add_liquidity') and tokens involved with historical prices. Additional 0.05 credits charged if data available.
        with_nft_sales (bool): Decoded NFT sales details including marketplace (e.g. Opensea) and cached media links. Additional 0.05 credits charged if data available.
        with_lending (bool): Decoded lending details including protocol (e.g. Aave), event (e.g. 'deposit') and tokens involved with prices. Additional 0.05 credits charged if data available.
        with_safe (bool): Include safe details.
        """
        success = False
        data: Optional[Response[TransactionResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                    
                if no_logs is not None:
                    url_params["no-logs"] = str(no_logs)
                    
                if with_dex is not None:
                    url_params["with-dex"] = str(with_dex)
                    
                if with_nft_sales is not None:
                    url_params["with-nft-sales"] = str(with_nft_sales)
                    
                if with_lending is not None:
                    url_params["with-lending"] = str(with_lending)
                
                if with_safe is not None:
                    url_params["with-safe"] = str(with_safe)

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/transaction_v2/{tx_hash}/", params=url_params, headers={
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

                data_class = TransactionResponse(data.data)
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
        
    async def get_all_transactions_for_address(self, chain_name: chain, wallet_address: str, quote_currency: Optional[quote] = None, no_logs: Optional[bool] = None, block_signed_at_asc: Optional[bool] = None, with_safe: Optional[bool] = None) -> AsyncIterable[Transaction]:
        """
        Commonly used to fetch and render the most recent transactions involving an address. Frequently seen in wallet applications.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        no_logs (bool): Omit log events.
        block_signed_at_asc (bool): Sort the transactions in ascending chronological order. By default, it's set to `false` and returns transactions in descending chronological order.
        with_safe (bool): Include safe details.
        """
        success = False
        response = None
        while not success:
            try:
                url_params = {}
                
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                
                if no_logs is not None:
                    url_params["no-logs"] = str(no_logs)
                
                if block_signed_at_asc is not None:
                    url_params["block-signed-at-asc"] = str(block_signed_at_asc)
                
                if with_safe is not None:
                    url_params["with-safe"] = str(with_safe)
                

                async for response in paginate_endpoint(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/transactions_v3/", self.__api_key, url_params, self.__debug):
                    yield response

                success = True
            except Exception as error:
                success = True
                raise Exception(error)

    def get_transactions_for_block(self, chain_name: chain, block_height: int, quote_currency: Optional[quote] = None, no_logs: Optional[bool] = None, with_safe: Optional[bool] = None) -> Response[TransactionsBlockResponse]:
        """
        Commonly used to fetch all transactions including their decoded log events in a block and further flag interesting wallets or transactions.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        block_height (int): The requested block height.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        no_logs (bool): Omit log events.
        with_safe (bool): Include safe details.
        """
        success = False
        data: Optional[Response[TransactionsBlockResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                    
                if no_logs is not None:
                    url_params["no-logs"] = str(no_logs)
                
                if with_safe is not None:
                    url_params["with-safe"] = str(with_safe)

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/block/{block_height}/transactions_v3/", params=url_params, headers={
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

                data_class = TransactionsBlockResponse(data.data)
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
        
    def get_transaction_summary(self, chain_name: chain, wallet_address: str) -> Response[TransactionsSummaryResponse]:
        """
        Commonly used to fetch the earliest and latest transactions, and the transaction count for a wallet. Calculate the age of the wallet and the time it has been idle and quickly gain insights into their engagement with web3.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        """
        success = False
        data: Optional[Response[TransactionsSummaryResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/transactions_summary/", params=url_params, headers={
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

                data_class = TransactionsSummaryResponse(data.data)
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

    def get_transactions_for_address_v3(self, chain_name: chain, wallet_address: str, page: int, quote_currency: Optional[quote] = None, no_logs: Optional[bool] = None, block_signed_at_asc: Optional[bool] = None, with_safe: Optional[bool] = None) -> Response[TransactionsResponse]:
        """
        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        page (int): The requested page, 0-indexed.
        quote_currency (string): The currency to convert. Supports `USD`, `CAD`, `EUR`, `SGD`, `INR`, `JPY`, `VND`, `CNY`, `KRW`, `RUB`, `TRY`, `NGN`, `ARS`, `AUD`, `CHF`, and `GBP`.
        no_logs (bool): Omit log events.
        block_signed_at_asc (bool): Sort the transactions in ascending chronological order. By default, it's set to `false` and returns transactions in descending chronological order.
        with_safe (bool): Include safe details.
        """
        success = False
        data: Optional[Response[TransactionsResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                
                if quote_currency is not None:
                    url_params["quote-currency"] = str(quote_currency)
                    
                if no_logs is not None:
                    url_params["no-logs"] = str(no_logs)
                    
                if block_signed_at_asc is not None:
                    url_params["block-signed-at-asc"] = str(block_signed_at_asc)
                    
                if with_safe is not None:
                    url_params["with-safe"] = str(with_safe)
                    
                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/address/{wallet_address}/transactions_v3/page/{page}/", params=url_params, headers={
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

                data_class = TransactionsResponse(data.data)
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
        
    
    