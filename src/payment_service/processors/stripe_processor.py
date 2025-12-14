import os
import stripe
from dotenv import load_dotenv
from stripe import StripeError 
from payment_service.commons import CustomerData, PaymentData, PaymentResponse
from .payment import PaymentProcessorProtocol
from .recurring import RecurringPaymentProcessorProtocol
from .refunds import RefundProcessorProtocol

_ = load_dotenv()

class StripePaymentProcessor(PaymentProcessorProtocol, RefundProcessorProtocol, RecurringPaymentProcessorProtocol):
    def process_transaction(self, customer_data: CustomerData, payment_data: PaymentData) -> PaymentResponse:
        stripe.api_key = os.getenv("STRIPE_API_KEY") 
        # Payment processing responsibility
        try:
            charge = stripe.Charge.create(
                amount=payment_data.amount,
                currency=payment_data.currency,
                source=payment_data.source,
                description="Charge for " + customer_data.name,
            )
            print("Payment successful.")
            print("Transaction_ID:", charge["id"])
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
                amount=payment_data.amount,
                transaction_id=None,
                message=str(e),
            )
    def refund_payment(self, transaction_id: str) -> PaymentResponse:
        stripe.api_key = os.getenv("STRIPE_API_KEY") 
        # Refund processing responsibility
        try:
            refund = stripe.Refund.create(
                charge=transaction_id,
            )
            print("Refund successful")
            return PaymentResponse(
                status=refund["status"],
                amount=refund["amount"],
                transaction_id=refund["id"],
                message="Refund successful",
            )
        except StripeError as e:
            print("Refund failed:", e)
            return PaymentResponse(
                status="failed",
                amount=0,
                transaction_id=None,
                message=str(e),
            )
    def setup_recurring_payment(self, customer_data: CustomerData, payment_data: PaymentData) -> PaymentResponse:
        print("Creating recurring payment for", customer_data.name)  