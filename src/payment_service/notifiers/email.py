from payment_service.commons import CustomerData, PaymentData
from .notifier import NotifierProtocol
from email.mime.text import MIMEText

class EmailNotifier(NotifierProtocol):
    def send_notification(self, customer_data: CustomerData, payment_data: PaymentData, transaction_id: str): 
        msg_body = f"This is a confirmation of your recent payment. \nAmount processed: {payment_data.currency} {payment_data.amount}. \nTransaction ID: {transaction_id}.\nThank you for your business!"
        msg = MIMEText(msg_body)
        msg["Subject"] = "Payment Confirmation"
        msg["From"] = "no-reply@example.com"
        msg["To"] = customer_data.contact_info.email  

        # server = smtplib.SMTP('smtp.localhost.com')
        # server.send_message(msg)
        # server.quit()
        print("Email sent to:", customer_data.contact_info.email) 
        print("Email body:", msg_body)