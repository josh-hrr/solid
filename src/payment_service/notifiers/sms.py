from dataclasses import dataclass
from payment_service.commons import CustomerData, PaymentData
from .notifier import NotifierProtocol

@dataclass 
class SMSNotifier(NotifierProtocol):
    gateway: str

    def send_notification(self, customer_data: CustomerData, payment_data: PaymentData, transaction_id: str):
        phone_number = customer_data.contact_info.phone
        if not phone_number:
            print("No phone number provided")
            return
        print(f"SMS sent to {phone_number} via {self.gateway}: Thank you for your payment! \nAmount processed: {payment_data.currency} {payment_data.amount}. \nTransaction ID: {transaction_id}.")
