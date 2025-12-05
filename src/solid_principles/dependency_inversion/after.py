import os
from dataclasses import dataclass, field

import stripe
from dotenv import load_dotenv
from stripe import Charge, StripeError 
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional, Protocol
import uuid

_ = load_dotenv()

# Type hinting for the payment response
class PaymentResponse(BaseModel):
    status: str
    amount: float
    transaction_id: str
    message: str
 

@dataclass
class CustomerValidation: 
    def validate(self, customer_data):
        # Validations responsibility
        if not customer_data.get("name"):
            print("Invalid customer data: missing name")
            raise ValueError("Invalid customer data: missing name") 
        if not customer_data.get("contact_info"):
            print("Invalid customer data: missing contact info")
            raise ValueError("Invalid customer data: missing contact info")   
        if not (customer_data.get("contact_info").get("email") or customer_data.get("contact_info").get("phone")):
            print("Invalid customer data: missing email or phone")
            raise ValueError("Invalid customer data: missing email or phone")
    
@dataclass
class PaymentDataValidator: 
    def validate(self, payment_data):
        # Validations responsibility
        if not payment_data.get("source"):
            print("Invalid payment data")
            raise ValueError("Invalid payment data")
class Notification(ABC):
    @abstractmethod
    def send_confirmation(self, customer_data):
        ...
@dataclass
class EmailNotification(Notification):
    def send_confirmation(self, customer_data): 
        # Notification responsibility 
            # import smtplib
            from email.mime.text import MIMEText 
            msg = MIMEText("Thank you for your payment.")
            msg["Subject"] = "Payment Confirmation"
            msg["From"] = "no-reply@example.com"
            msg["To"] = customer_data["contact_info"].get("email", None) 
            # server = smtplib.SMTP("localhost")
            # server.send_message(msg)
            # server.quit()
            print("Email sent to", customer_data["contact_info"]["email"]) 

@dataclass
class SMSNotification(Notification):
    sms_gateway: str = field(default="the custom SMS Gateway")
    def send_confirmation(self, customer_data):
        # Notification responsibility 
        phone_number = customer_data["contact_info"].get("phone", None) 
        sms_gateway = self.sms_gateway
        print(
            f"send the sms using {sms_gateway}: SMS sent to {phone_number}: Thank you for your payment."
        )
@dataclass
class TransactionLogger:
    def log(self, customer_data, payment_data, charge):
         # Logging responsibility
        with open("transactions.log", "a") as log_file:
            log_file.write(f"{customer_data['name']} paid {payment_data['amount']}\n")
            log_file.write(f"Payment status: {charge.status}\n")

class PaymentProcessor(ABC):
    @abstractmethod
    def process_transaction(self, customer_data, payment_data) -> PaymentResponse:
        ...   
class RefundTransactionProcessor(ABC):
    @abstractmethod
    def refund_transaction(self, transaction_id) -> PaymentResponse:
        ... 
class CreateRecurringPaymentProcessor(ABC):
    @abstractmethod
    def create_recurring_payment(self, customer_data, payment_data) -> PaymentResponse:
        ...

@dataclass
class StripePaymentProcessor(PaymentProcessor, RefundTransactionProcessor, CreateRecurringPaymentProcessor):
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
    def refund_transaction(self, transaction_id) -> PaymentResponse:
        print("Refunding transaction", transaction_id)
    def create_recurring_payment(self, customer_data, payment_data) -> PaymentResponse:
        print("Creating recurring payment for", customer_data["name"])

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
    ''' code below is not actually needed in this class, 
     it was removed to comply with the Interface Segregation Principle 
     Concept: a class should not depend on methods that DOES NOT implement.
    '''
    # def refund_transaction(self, transaction_id) -> PaymentResponse:
    #     raise NotImplementedError("Refunding transactions is not supported for offline payments")
    # def create_recurring_payment(self, customer_data, payment_data) -> PaymentResponse:
    #     raise NotImplementedError("Creating recurring payments is not supported for offline payments")

@dataclass
class PaymentService:
    # dependency_inversion: high-levl class should not depend on low-level class. 
    # class does not need to instantiate low-level classes, should follow Protocol contract.
    customer_validator: CustomerValidation
    payment_validator: PaymentDataValidator
    payment_processor: PaymentProcessor
    notifier: Notification
    logger: TransactionLogger
    recurring_processor: Optional[CreateRecurringPaymentProcessor] = None
    refund_processor: Optional[RefundTransactionProcessor] = None

    def process_transaction(self, customer_data, payment_data) -> Charge:
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

if __name__ == "__main__":
    # Setup Validators
    customer_validator = CustomerValidation()
    payment_validator = PaymentDataValidator()
    #Logger
    transaction_logger = TransactionLogger()
    # Setup payment processors
    stripe_processor = StripePaymentProcessor()
    offline_processor = OfflinePaymentProcessor() 
    # Setup notofication types
    sms_notification = SMSNotification(sms_gateway="twilio")
    email_notification = EmailNotification() 
    # Initialize PaymentService with Stripe and EmailNotification
    payment_processor_email = PaymentService(
        customer_validator=customer_validator,
        payment_validator=payment_validator, 
        payment_processor=stripe_processor, 
        notifier=email_notification,
        refund_processor=stripe_processor,
        recurring_processor=stripe_processor,
        logger=transaction_logger
        ) 
    # Initialize PaymentService with Stripe and SMSNotification 
    payment_processor_sms = PaymentService(
        customer_validator=customer_validator,
        payment_validator=payment_validator, 
        payment_processor=stripe_processor,
        notifier=sms_notification,
        logger=transaction_logger
    ) 
    # Setup the customer data and payment data
    customer_data_with_email = {
        "name": "John Doe",
        "contact_info": {"email": "e@mail.com"},
    }
    customer_data_with_phone = {
        "name": "Platzi Python",
        "contact_info": {"phone": "1234567890"},
    }
    # Setup payment data
    payment_data = {"amount": 500, "source": "tok_mastercard", "cvv": 123}

    print("\nProcessing payment_processor_email")
    payment_processor_email.process_transaction(customer_data_with_email, payment_data)
    print("\nProcessing payment_processor_sms")
    sms_payment_response=payment_processor_sms.process_transaction(customer_data_with_phone, payment_data)

    # Processing a Refund using Stripe
    print("\nProcessing a Refund using Stripe")
    transaction_id_to_refund = sms_payment_response.transaction_id
    if transaction_id_to_refund:
        payment_processor_email.refund_transaction(transaction_id_to_refund)
    
    # Using OfflinePaymentProcessor with EmailNotification
    print("\nUsing OfflinePaymentProcessor with EmailNotification")
    offline_payment_service = PaymentService(
        customer_validator=customer_validator,
        payment_validator=payment_validator, 
        payment_processor=offline_processor, 
        notifier=email_notification, 
        logger=transaction_logger)
    offline_payment_response = offline_payment_service.process_transaction(
        customer_data_with_email, payment_data
    )

    # Attempt to refund using offline processor (will fail)
    print("\nAttempt to refund using offline processor (will fail)")
    try:
        if offline_payment_response.transaction_id:
            offline_payment_service.process_refund(
                offline_payment_response.transaction_id
            )
    except Exception as e:
        print(f"Refund failed and PaymentService raised an exception: {e}")

    # Attempt to set up recurring payment using offline processor (will fail)
    print("\nAttempt to set up recurring payment using offline processor (will fail)")
    try:
        offline_payment_service.create_recurring_payment(customer_data_with_email, payment_data)

    except Exception as e:
        print(
            f"Recurring payment setup failed and PaymentService raised an exception {e}"
        )
    
    # Transaction that errors because of the cardType is invalid.
    print("\nTransaction that errors because of the cardType is invalid.")
    try: 
        invalid_payment_data = {"amount": 100, "source": "tok_radarBlock"} 
        payment_processor_email.process_transaction(
            customer_data_with_email, invalid_payment_data
        )
    except Exception as e:
        print(f"Payment failed and PaymentService raised an exception: {e}")
    
    # Set up create_recurring_payment for Stripe and EmailNotification 
    print("\nSet up create_recurring_payment for Stripe and EmailNotification")
    payment_processor_email.create_recurring_payment(
        customer_data_with_email, payment_data
    )
