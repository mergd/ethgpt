from datetime import datetime
from typing import List, Optional
import requests
from .util.back_off import ExponentialBackoff
from .util.api_helper import check_and_modify_response, paginate_endpoint, Response
from .util.types import chain, quote, user_agent
from .util.debugger import debug_output


class ApprovalsResponse:
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
    items: List["TokensApprovalItem"]
    """ List of response items. """

    def __init__(self, data):
        self.address = data["address"]
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.quote_currency = data["quote_currency"]
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.items = [TokensApprovalItem(item_data) for item_data in data["items"]]

class TokensApprovalItem:
    token_address: Optional[str]
    """ The address for the token that has approvals. """
    token_address_label: Optional[str]
    """ The name for the token that has approvals. """
    ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    contract_decimals: Optional[int]
    """ Use contract decimals to format the token balance for display purposes - divide the balance by `10^{contract_decimals}`. """
    logo_url: Optional[str]
    """ The contract logo URL. """
    quote_rate: Optional[float]
    """ The exchange rate for the requested quote currency. """
    balance: Optional[int]
    """ Wallet balance of the token. """
    balance_quote: Optional[float]
    """ Value of the wallet balance of the token. """
    pretty_balance_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """
    value_at_risk: Optional[str]
    """ Total amount at risk across all spenders. """
    value_at_risk_quote: Optional[float]
    """ Value of total amount at risk across all spenders. """
    pretty_value_at_risk_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """
    spenders: Optional[List["TokenSpenderItem"]]
    """ Contracts with non-zero approvals for this token. """

    def __init__(self, data):
        self.token_address = data["token_address"] if "token_address" in data and data["token_address"] is not None else None
        self.token_address_label = data["token_address_label"] if "token_address_label" in data and data["token_address_label"] is not None else None
        self.ticker_symbol = data["ticker_symbol"] if "ticker_symbol" in data and data["ticker_symbol"] is not None else None
        self.contract_decimals = int(data["contract_decimals"]) if "contract_decimals" in data and data["contract_decimals"] is not None else None
        self.logo_url = data["logo_url"] if "logo_url" in data and data["logo_url"] is not None else None
        self.quote_rate = data["quote_rate"] if "quote_rate" in data and data["quote_rate"] is not None else None
        self.balance = int(data["balance"]) if "balance" in data and data["balance"] is not None else None
        self.balance_quote = data["balance_quote"] if "balance_quote" in data and data["balance_quote"] is not None else None
        self.pretty_balance_quote = data["pretty_balance_quote"] if "pretty_balance_quote" in data and data["pretty_balance_quote"] is not None else None
        self.value_at_risk = data["value_at_risk"] if "value_at_risk" in data and data["value_at_risk"] is not None else None
        self.value_at_risk_quote = data["value_at_risk_quote"] if "value_at_risk_quote" in data and data["value_at_risk_quote"] is not None else None
        self.pretty_value_at_risk_quote = data["pretty_value_at_risk_quote"] if "pretty_value_at_risk_quote" in data and data["pretty_value_at_risk_quote"] is not None else None
        self.spenders = [TokenSpenderItem(item_data) for item_data in data["spenders"]] if "spenders" in data and data["spenders"] is not None else None

class TokenSpenderItem:
    block_height: Optional[int]
    """ The height of the block. """
    tx_offset: Optional[int]
    """ The offset is the position of the tx in the block. """
    log_offset: Optional[int]
    """ The offset is the position of the log entry within an event log." """
    block_signed_at: Optional[datetime]
    """ The block signed timestamp in UTC. """
    tx_hash: Optional[str]
    """ Most recent transaction that updated approval amounts for the token. """
    spender_address: Optional[str]
    """ Address of the contract with approval for the token. """
    spender_address_label: Optional[str]
    """ Name of the contract with approval for the token. """
    allowance: Optional[str]
    """ Remaining number of tokens granted to the spender by the approval. """
    allowance_quote: Optional[float]
    """ Value of the remaining allowance specified by the approval. """
    pretty_allowance_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """
    value_at_risk: Optional[str]
    """ Amount at risk for spender. """
    value_at_risk_quote: Optional[float]
    """ Value of amount at risk for spender. """
    pretty_value_at_risk_quote: Optional[str]
    """ A prettier version of the quote for rendering purposes. """
    risk_factor: Optional[str]

    def __init__(self, data):
        self.block_height = int(data["block_height"]) if "block_height" in data and data["block_height"] is not None else None
        self.tx_offset = int(data["tx_offset"]) if "tx_offset" in data and data["tx_offset"] is not None else None
        self.log_offset = int(data["log_offset"]) if "log_offset" in data and data["log_offset"] is not None else None
        self.block_signed_at = datetime.fromisoformat(data["block_signed_at"]) if "block_signed_at" in data and data["block_signed_at"] is not None else None
        self.tx_hash = data["tx_hash"] if "tx_hash" in data and data["tx_hash"] is not None else None
        self.spender_address = data["spender_address"] if "spender_address" in data and data["spender_address"] is not None else None
        self.spender_address_label = data["spender_address_label"] if "spender_address_label" in data and data["spender_address_label"] is not None else None
        self.allowance = data["allowance"] if "allowance" in data and data["allowance"] is not None else None
        self.allowance_quote = data["allowance_quote"] if "allowance_quote" in data and data["allowance_quote"] is not None else None
        self.pretty_allowance_quote = data["pretty_allowance_quote"] if "pretty_allowance_quote" in data and data["pretty_allowance_quote"] is not None else None
        self.value_at_risk = data["value_at_risk"] if "value_at_risk" in data and data["value_at_risk"] is not None else None
        self.value_at_risk_quote = data["value_at_risk_quote"] if "value_at_risk_quote" in data and data["value_at_risk_quote"] is not None else None
        self.pretty_value_at_risk_quote = data["pretty_value_at_risk_quote"] if "pretty_value_at_risk_quote" in data and data["pretty_value_at_risk_quote"] is not None else None
        self.risk_factor = data["risk_factor"] if "risk_factor" in data and data["risk_factor"] is not None else None

class NftApprovalsResponse:
    updated_at: datetime
    """ The timestamp when the response was generated. Useful to show data staleness to users. """
    chain_id: int
    """ The requested chain ID eg: `1`. """
    chain_name: str
    """ The requested chain name eg: `eth-mainnet`. """
    address: str
    """ The requested address. """
    items: List["NftApprovalsItem"]
    """ List of response items. """

    def __init__(self, data):
        self.updated_at = datetime.fromisoformat(data["updated_at"])
        self.chain_id = int(data["chain_id"])
        self.chain_name = data["chain_name"]
        self.address = data["address"]
        self.items = [NftApprovalsItem(item_data) for item_data in data["items"]]

class NftApprovalsItem:
    contract_address: Optional[str]
    """ Use the relevant `contract_address` to lookup prices, logos, token transfers, etc. """
    contract_address_label: Optional[str]
    """ The label of the contract address. """
    contract_ticker_symbol: Optional[str]
    """ The ticker symbol for this contract. This field is set by a developer and non-unique across a network. """
    token_balances: Optional[List["NftApprovalBalance"]]
    """ List of asset balances held by the user. """
    spenders: Optional[List["NftApprovalSpender"]]
    """ Contracts with non-zero approvals for this token. """

    def __init__(self, data):
        self.contract_address = data["contract_address"] if "contract_address" in data and data["contract_address"] is not None else None
        self.contract_address_label = data["contract_address_label"] if "contract_address_label" in data and data["contract_address_label"] is not None else None
        self.contract_ticker_symbol = data["contract_ticker_symbol"] if "contract_ticker_symbol" in data and data["contract_ticker_symbol"] is not None else None
        self.token_balances = [NftApprovalBalance(item_data) for item_data in data["token_balances"]] if "token_balances" in data and data["token_balances"] is not None else None
        self.spenders = [NftApprovalSpender(item_data) for item_data in data["spenders"]] if "spenders" in data and data["spenders"] is not None else None

class NftApprovalBalance:
    token_id: Optional[int]
    """ The token's id. """
    token_balance: Optional[int]
    """ The NFT's token balance. """

    def __init__(self, data):
        self.token_id = int(data["token_id"]) if "token_id" in data and data["token_id"] is not None else None
        self.token_balance = int(data["token_balance"]) if "token_balance" in data and data["token_balance"] is not None else None
            

class NftApprovalSpender:
    block_height: Optional[int]
    """ The height of the block. """
    tx_offset: Optional[int]
    """ The offset is the position of the tx in the block. """
    log_offset: Optional[int]
    """ The offset is the position of the log entry within an event log." """
    block_signed_at: Optional[datetime]
    """ The block signed timestamp in UTC. """
    tx_hash: Optional[str]
    """ Most recent transaction that updated approval amounts for the token. """
    spender_address: Optional[str]
    """ Address of the contract with approval for the token. """
    spender_address_label: Optional[str]
    """ Name of the contract with approval for the token. """
    token_ids_approved: Optional[str]
    """ The token ids approved. """
    allowance: Optional[str]
    """ Remaining number of tokens granted to the spender by the approval. """

    def __init__(self, data):
        self.block_height = int(data["block_height"]) if "block_height" in data and data["block_height"] is not None else None
        self.tx_offset = int(data["tx_offset"]) if "tx_offset" in data and data["tx_offset"] is not None else None
        self.log_offset = int(data["log_offset"]) if "log_offset" in data and data["log_offset"] is not None else None
        self.block_signed_at = datetime.fromisoformat(data["block_signed_at"]) if "block_signed_at" in data and data["block_signed_at"] is not None else None
        self.tx_hash = data["tx_hash"] if "tx_hash" in data and data["tx_hash"] is not None else None
        self.spender_address = data["spender_address"] if "spender_address" in data and data["spender_address"] is not None else None
        self.spender_address_label = data["spender_address_label"] if "spender_address_label" in data and data["spender_address_label"] is not None else None
        self.token_ids_approved = data["token_ids_approved"] if "token_ids_approved" in data and data["token_ids_approved"] is not None else None
        self.allowance = data["allowance"] if "allowance" in data and data["allowance"] is not None else None


class SecurityService:
    __api_key: str
    __debug: Optional[bool]
    def __init__(self, api_key: str, debug: Optional[bool] = False):
        self.__api_key = api_key
        self.__debug = debug


    def get_approvals(self, chain_name: chain, wallet_address: str) -> Response[ApprovalsResponse]:
        """
        Commonly used to get a list of approvals across all token contracts categorized by spenders for a wallet’s assets.

        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        """
        success = False
        data: Optional[Response[ApprovalsResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}

                start_time = None
                if self.__debug:
                    start_time = datetime.now()

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/approvals/{wallet_address}/", params=url_params, headers={
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

                data_class = ApprovalsResponse(data.data)
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
        
        
    def get_nft_approvals(self, chain_name: chain, wallet_address: str) -> Response[NftApprovalsResponse]:
        """
        Parameters:

        chain_name (string): The chain name eg: `eth-mainnet`.
        wallet_address (str): The requested address. Passing in an `ENS`, `RNS`, `Lens Handle`, or an `Unstoppable Domain` resolves automatically.
        """
        success = False
        data: Optional[Response[NftApprovalsResponse]] = None
        response = None
        backoff = ExponentialBackoff(self.__api_key, self.__debug)
        while not success:
            try:
                url_params = {}
                

                response = requests.get(f"https://api.covalenthq.com/v1/{chain_name}/nft/approvals/{wallet_address}/", params=url_params, headers={
                    "Authorization": f"Bearer {self.__api_key}",
                    "X-Requested-With": user_agent
                })

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
                
                data_class = NftApprovalsResponse(data.data)
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
        
    
    
    