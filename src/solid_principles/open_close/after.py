import os
from dataclasses import dataclass, field

import stripe
from dotenv import load_dotenv
from stripe import Charge, StripeError 
from abc import ABC, abstractmethod

_ = load_dotenv()

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

class SMSNotification(Notification):
    def send_confirmation(self, customer_data):
        # Notification responsibility 
        phone_number = customer_data["contact_info"].get("phone", None) 
        sms_gateway = "the custom SMS Gateway"
        print(
            f"send the sms using {sms_gateway}: SMS sent to {phone_number}: Thank you for your payment."
        )
@dataclass
class TransactionLogger:
    def log(self, customer_data, payment_data, charge):
         # Logging responsibility
        with open("transactions.log", "a") as log_file:
            log_file.write(f"{customer_data['name']} paid {payment_data['amount']}\n")
            log_file.write(f"Payment status: {charge['status']}\n")
class PaymentProcessor(ABC):
    @abstractmethod
    def process_transaction(self, customer_data, payment_data) -> Charge:
        ...
@dataclass
class StripePaymentProcessor(PaymentProcessor):
    def process_transaction(self, customer_data, payment_data) -> Charge:  
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
        except StripeError as e:
            print("Payment failed:", e)
            raise e   

        return charge
@dataclass
class PaymentService:
    customer_validator = CustomerValidation()
    payment_validator = PaymentDataValidator()
    payment_processor: PaymentProcessor = field(default_factory=StripePaymentProcessor)
    notifier: Notification = field(default_factory=EmailNotification)
    logger = TransactionLogger()

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

if __name__ == "__main__":
    sms_notification = SMSNotification()
    payment_processor = PaymentService(notifier=sms_notification)

    customer_data_with_email = {
        "name": "John Doe",
        "contact_info": {"email": "e@mail.com"},
    }
    customer_data_with_phone = {
        "name": "Platzi Python",
        "contact_info": {"phone": "1234567890"},
    }
 
    payment_data = {"amount": 500, "source": "tok_mastercard", "cvv": 123}

    payment_processor.process_transaction(customer_data_with_email, payment_data)
    payment_processor.process_transaction(customer_data_with_phone, payment_data)

 