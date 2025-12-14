from .commons import CustomerData, PaymentData
from .service import PaymentService
from .processors import StripePaymentProcessor
from .notifiers import EmailNotifier, SMSNotifier
from .loggers import TransactionLogger
from .validators import CustomerValidator, PaymentDataValidator

if __name__ == "__main__":
    stripe_payment_processor = StripePaymentProcessor()
    email_notifier = EmailNotifier()
    sms_notifier = SMSNotifier(gateway="Twilio")
    customer_validator = CustomerValidator()
    payment_data_validator = PaymentDataValidator()
    logger = TransactionLogger()
    
    email_service = PaymentService(
        payment_processor=stripe_payment_processor,
        notifier=email_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_data_validator,
        logger=logger,
    )
    sms_service = PaymentService(
        payment_processor=stripe_payment_processor,
        notifier=sms_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_data_validator,
        logger=logger,
    )
    # Example usage
    # Setup the customer data and payment data
    customer_data_with_email = CustomerData(
        name="John Doe",
        contact_info={
            "email": "test@test.com"
        }
    )
    customer_data_with_phone = CustomerData(
        name="Jane Smith",
        contact_info={
            "phone": "+1234567890"
        }
    )
    # Setup payment data
    payment_data_email = PaymentData(
        amount=50,
        source="tok_mastercard",
        currency="USD"
    )
    payment_data_sms = PaymentData(
        amount=150,
        source="tok_mastercard",
        currency="USD"
    )
    # Process a transaction
    print("\nProcessing payment_processor_email")
    email_service.process_transaction(customer_data_with_email, payment_data_email)
    print("\nProcessing payment_processor_sms")
    sms_payment_response = sms_service.process_transaction(customer_data_with_phone, payment_data_sms)