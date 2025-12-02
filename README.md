# Stripe Payment Processor - SOLID Principles Made Simple

This project demonstrates SOLID principles through practical examples using a real life project by building a Stripe payment processing system.

## SOLID Principles Covered

### 1. Single Responsibility (SRP)

**Principle**: A class should have only one reason to change, meaning it should have only one responsibility.

#### Before (Violating SRP)
In `src/solid_principles/single_responsability/before.py`, the `PaymentProcessor` class handles multiple responsibilities:
- Customer data validation
- Payment data validation
- Payment processing with Stripe integration
- Sending notifications via Email/SMS
- Logging transactions

#### After (Following SRP)
In `src/solid_principles/single_responsability/after.py`, responsibilities are separated into dedicated classes:
- `CustomerValidation` - validates customer data
- `PaymentDataValidator` - validates payment data
- `StripePaymentProcessor` - handles payment processing
- `Notifier` - handles notifications
- `TransactionLogger` - handles logging
- `PaymentService` - orchestrates the process by using the above classes 

---

### 2. Open/Closed (OCP)

**Principle**: Software entities should be open for extension but closed for modification. You should be able to add new functionality without changing existing code.

#### Before (Violating OCP)
In `src/solid_principles/open_close/before.py`, the `Notifier` class contains a function send_confirmation that contains the logic for both email and SMS notifications. This means, if a new notification method is required (e.g., push notifications), we would need to modify the function send_confirmation in the existing `Notifier` class to include the new logic.

#### After (Following OCP)
In `src/solid_principles/open_close/after.py`, the design uses:
- `Notification` abstract base class - includes the send_confirmation function and @abstractmethod decorator so it is required by the classes that extend this class to implement the @abstractmethod.
- `EmailNotification` - extends Notification
- `SMSNotification` - extends Notification
- `PaymentProcessor` abstract base class - allows different payment processors
- `StripePaymentProcessor` - extends Stripe payment processing

The `PaymentService` class accepts `Notification` and `PaymentProcessor` as types, allowing you to:
- Instantiate new notification types (e.g., `PushNotification`) without modifying existing code inside each notification type.
- Instantiate new payment processors (e.g., `PayPalPaymentProcessor`) without modifying existing code inside each payment type.

Key takeaway:
We extend functionality by creating new classes that extends the abstract classes, rather than modifying existing functionality.

---

### 3. Liskov Substitution (LSP)

**Principle**: Subclasses should be substituted by base class.

## Project Structure

```
src/
└── solid_principles/
    ├── single_responsability/
    │   ├── before.py  # Violates SRP
    │   └── after.py   # Follows SRP
    └── open_close/
        ├── before.py  # Violates OCP
        └── after.py   # Follows OCP
```

## Running the Examples

Each file can be run independently:

```bash
# Single Responsibility examples
python src/solid_principles/single_responsability/before.py
python src/solid_principles/single_responsability/after.py

# Open/Closed examples
python src/solid_principles/open_close/before.py
python src/solid_principles/open_close/after.py
```

## Key Takeaways

- **Single Responsibility**: Break down classes into smaller, focused components.
- **Open/Closed**: Use abstractions (abstract classes) to allow extension without modification of existing functionality.
- Both principles lead to more maintainable, testable, and flexible code.

