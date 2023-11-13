from .services.security_service import SecurityService
from .services.balance_service import BalanceService
from .services.base_service import BaseService
from .services.nft_service import NftService
from .services.pricing_service import PricingService
from .services.transaction_service import TransactionService
from .services.xyk_service import XykService

class Client:
    """ Client Class """

    security_service: SecurityService

    balance_service: BalanceService

    base_service: BaseService

    nft_service: NftService

    pricing_service: PricingService

    transaction_service: TransactionService

    xyk_service: XykService

    def __init__(self, api_key: str):

        self.security_service = SecurityService(api_key)
        self.balance_service = BalanceService(api_key)
        self.base_service = BaseService(api_key)
        self.nft_service = NftService(api_key)
        self.pricing_service = PricingService(api_key)
        self.transaction_service = TransactionService(api_key)
        self.xyk_service = XykService(api_key)
