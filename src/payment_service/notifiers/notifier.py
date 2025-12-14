from typing import Protocol
from payment_service.commons import CustomerData, PaymentData

class NotifierProtocol(Protocol):
    """Protocol for sending notifications.

    This protocol defines the interface for notification.
    Should provide a method 'send_notification' that returns ConsumerData.
    """
    def send_notifcation(self, customer_data: CustomerData, payment_data: PaymentData, transaction_id: str) -> None:
        ...