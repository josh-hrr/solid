from .commons import PaymentData
from .processors import PaymentProcessorProtocol, OfflinePaymentProcessor, StripePaymentProcessor
from .commons import PaymentType

class PaymentProcessorFactory:
    ...

    @staticmethod
    def create_payment_processor(payment_data: PaymentData) -> PaymentProcessorProtocol:
        match payment_data.type:
            case PaymentType.OFFLINE:
                return OfflinePaymentProcessor()
            case PaymentType.ONLINE:
                match payment_data.currency:
                    case "USD":
                        return StripePaymentProcessor()
                    case _:
                        return "Unsupported currency for online payments"
            case _:
                raise ValueError("Unsupported payment type")