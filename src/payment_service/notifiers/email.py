from payment_service.commons import CustomerData
from .notifier import NotifierProtocol

class EmailNotifier(NotifierProtocol):
    def send_notification(self, customer_data: CustomerData):
        from email.mime.text import MIMEText

        msg = MIMEText("Thank you for your payment.")
        msg["Subject"] = "Payment Confirmation"
        msg["From"] = "no-reply@example.com"
        msg["To"] = customer_data.contact_info.email 

        # server = smtplib.SMTP('smtp.localhost.com')
        # server.send_message(msg)
        # server.quit()
        print("Email sent to", customer_data.contact_info.email)