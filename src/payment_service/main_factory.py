from .commons import ContactInfo, CustomerData, PaymentData, PaymentType
from .service import PaymentService
from .processors import StripePaymentProcessor
from .notifiers import EmailNotifier, SMSNotifier
from .loggers import TransactionLogger
from .validators import CustomerValidator, PaymentDataValidator


def get_notifier_strategy(customer_data: CustomerData) -> EmailNotifier | SMSNotifier:
    """Factory function to select the appropriate notification strategy based on customer data."""
    if customer_data.contact_info.email:
        return EmailNotifier()
    if customer_data.contact_info.phone:
        return SMSNotifier(gateway="SMSTwilio") 
    raise ValueError("No valid notification strategy found for customer")


if __name__ == "__main__":
    # Setup dependencies to test FactoryMethod
    payment_processor = StripePaymentProcessor()
    customer_validator = CustomerValidator()
    payment_validator = PaymentDataValidator()
    logger = TransactionLogger()
    
    # Create customer and payment data
    customer_data = CustomerData(
        name="John Doe",
        contact_info=ContactInfo(email="john.doe@example.com", phone="+1234567890")
    )
    payment_data = PaymentData(
        amount=100,
        source="tok_mastercard",
        currency="USD"
    )
    
    # Initialize with email notification strategy (selected based on customer data)
    initial_notifier = get_notifier_strategy(customer_data)
    
    # Create PaymentService with initial strategy
    service = PaymentService.create_with_payment_processor(
        payment_data=payment_data,
        notifier=initial_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_validator,
        logger=logger,
    )

    # Process transaction with FactoryMethod created processor
    print("=" * 60)
    print("FACTORY METHOD PATTERN DEMONSTRATION")
    print("=" * 60)
    print("\n[1] Processing transaction with FactoryMethod created processor:")
    service.process_transaction(customer_data, payment_data)

    # Changing PaymentType from ONLINE to OFFLINE
    print("\n[2] Changing PaymentType from ONLINE to OFFLINE:")
    payment_data.type = PaymentType.OFFLINE
    service_offline = PaymentService.create_with_payment_processor(
        payment_data=payment_data,
        notifier=initial_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_validator,
        logger=logger,
    )
    offline_test=service_offline.process_transaction(customer_data, payment_data)
    print("Offline transaction response:", offline_test.message)

    