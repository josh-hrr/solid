from typing_extensions import Protocol
from payment_service.commons import RefundResponse

class RefundProcessorProtocol(Protocol):
    """Protocol for processing refunds."""

    def refund_payment(self, transaction_id: str) -> RefundResponse:
        ...