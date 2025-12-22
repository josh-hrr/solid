from dataclasses import dataclass
from typing import Optional, Self
from stripe import StripeError 
from .commons import PaymentResponse, PaymentData
from .processors import PaymentProcessorProtocol, RecurringPaymentProcessorProtocol, RefundProcessorProtocol
from .notifiers import NotifierProtocol
from .validators import CustomerValidator, PaymentDataValidator
from .loggers import TransactionLogger 
from .factory import PaymentProcessorFactory

@dataclass
class PaymentService:
    # dependency_inversion: high-levl class should not depend on low-level class. 
    # class does not need to instantiate low-level classes, should follow Protocol contract.
    customer_validator: CustomerValidator
    payment_validator: PaymentDataValidator
    payment_processor: PaymentProcessorProtocol
    notifier: NotifierProtocol
    logger: TransactionLogger
    recurring_processor: Optional[RecurringPaymentProcessorProtocol] = None
    refund_processor: Optional[RefundProcessorProtocol] = None

    @classmethod
    def create_with_payment_processor(cls, payment_data: PaymentData, **kwargs) -> Self:
        try:
            processor = PaymentProcessorFactory.create_payment_processor(payment_data)
            return cls(payment_processor=processor, **kwargs)
        except ValueError as e:
            print("Error creating PaymentService:", e)

    def set_notifier(self, notifier: NotifierProtocol):
        print(f"Changing the notifier implementation {notifier.__class__.__name__}")
        self.notifier = notifier

    def process_transaction(self, customer_data, payment_data) -> PaymentResponse:
        try:
            self.customer_validator.validate(customer_data)
        except ValueError as e:
            raise e 
        try:
            self.payment_validator.validate(payment_data)
        except ValueError as e:
            raise e  
        try:
            charge = self.payment_processor.process_transaction(customer_data, payment_data)
            self.notifier.send_notification(customer_data, payment_data, charge.transaction_id)
            self.logger.log_transaction(customer_data, payment_data, charge)
            return charge
        except StripeError as e:
            raise e
    def refund_transaction(self, transaction_id) -> PaymentResponse:
        if self.refund_processor:
            return self.refund_processor.refund_transaction(transaction_id)
        else:
            raise NotImplementedError("Refunding transactions is not supported by the current payment processor")
    def create_recurring_payment(self, customer_data, payment_data) -> PaymentResponse:
        if self.recurring_processor:
            return self.recurring_processor.create_recurring_payment(customer_data, payment_data)
        else:
            raise NotImplementedError("Creating recurring payments is not supported by the current payment processor")