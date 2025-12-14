from typing import Protocol
from payment_service.commons import CustomerData, PaymentData, PaymentResponse

class PaymentProcessorProtocol(Protocol):
    """Protocol for processing payments.

    This protocol defines the interface for payment processing.
    Should provide methods for processing payments.
    """ 
    def process_transaction(self, customer_data: CustomerData, payment_data: PaymentData) -> PaymentResponse:
        ...