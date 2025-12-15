from .commons import ContactInfo, CustomerData, PaymentData
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
    # Setup dependencies
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
    service = PaymentService(
        payment_processor=payment_processor,
        notifier=initial_notifier,
        customer_validator=customer_validator,
        payment_validator=payment_validator,
        logger=logger,
    )
    
    print("=" * 60)
    print("STRATEGY PATTERN DEMONSTRATION")
    print("=" * 60)
    
    # Process transaction with initial strategy (Email)
    print("\n[1] Processing transaction with Email notification strategy:")
    service.process_transaction(customer_data, payment_data)
    
    # Strategy Pattern: Change strategy at runtime
    print("\n[2] Changing notification strategy to SMS at runtime:")
    service.set_notifier(SMSNotifier(gateway="SMSTwilio"))
    
    # Process another transaction with new strategy (SMS)
    print("\n[3] Processing transaction with SMS notification strategy:")
    service.process_transaction(customer_data, payment_data)
    
    # Demonstrate switching back to Email strategy
    print("\n[4] Switching back to Email notification strategy:")
    service.set_notifier(EmailNotifier())
    service.process_transaction(customer_data, payment_data)
    
    print("\n" + "=" * 60)
    print("Key takeaway: The same PaymentService can use different")
    print("notification strategies without modifying its code!")
    print("=" * 60)
    