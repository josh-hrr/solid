from abc import ABC, abstractmethod
from dataclasses import dataclass
from pydantic import BaseModel
import stripe 
from stripe import StripeError 
import uuid  

# Type hinting for the payment response
class PaymentResponse(BaseModel):
    status: str
    amount: float
    transaction_id: str
    message: str
# Abstraction
class PaymentProcessor(ABC):  
    @abstractmethod
    def process_transaction(self, customer_data, payment_data) -> PaymentResponse:
        ...
# Payment Type 1
@dataclass
class StripePaymentProcessor(PaymentProcessor):
    def process_transaction(self, customer_data, payment_data) -> PaymentResponse:  
        stripe.api_key = os.getenv("STRIPE_API_KEY") 
        # Payment processing responsibility
        try:
            charge = stripe.Charge.create(
                amount=payment_data["amount"],
                currency="usd",
                source=payment_data["source"],
                description="Charge for " + customer_data["name"],
            )
            print("Payment successful")
            return PaymentResponse(
                status=charge["status"],
                amount=charge["amount"],
                transaction_id=charge["id"],
                message="Payment successful",
            )
        except StripeError as e:
            print("Payment failed:", e)
            return PaymentResponse(
                status="failed",
                amount=payment_data["amount"],
                transaction_id=None,
                message=str(e),
            )
# Payment Type 2
@dataclass
class OfflinePaymentProcessor(PaymentProcessor):
    def process_transaction(self, customer_data, payment_data) -> PaymentResponse:
        print("Processing offline payment for", customer_data["name"])
        return PaymentResponse(
            status="success",
            amount=payment_data["amount"],
            transaction_id=str(uuid.uuid4()),
            message="Offline payment successful"
        )
# Here is where the magic happens:
# In the below class 'PaymentService', the Dependency 'payment_processor' is an Abstraction of PaymentProcessor, which means once PaymentService is instantiated it can have as any Payment Type as argument, but, it follows PaymentProcessor contract.
@dataclass
class PaymentService:
    # The high-level class depends on the PaymentProcessor abstraction instead of concrete implementations.
    # This allows swapping StripePaymentProcessor, OfflinePaymentProcessor, etc. without modifying PaymentService,
    # preserving OCP and avoiding tight coupling — otherwise changing payment logic would force modifying this class,
    # breaking both OCP and DIP.
    payment_processor: PaymentProcessor  
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
            self.notifier.send_confirmation(customer_data)
            self.logger.log(customer_data, payment_data, charge)
            return charge
        except StripeError as e:
            raise e

# Usage, first we instantiate the Payment Type 1 and 2
stripe_payment_processor = StripePaymentProcessor()
offline_payment_processor = OfflinePaymentProcessor()
 
# Any implementation of PaymentProcessor can be swapped here without modifying PaymentService.
stripe = PaymentService(payment_processor=stripe_payment_processor)
offline = PaymentService(payment_processor=offline_payment_processor)