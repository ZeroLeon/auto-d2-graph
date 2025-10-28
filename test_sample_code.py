"""
Sample Python code for testing the D2 diagram generator.
This represents a simple e-commerce system with multiple classes and relationships.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import json


class User(ABC):
    """Abstract base class for users."""

    def __init__(self, user_id: str, name: str, email: str):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.created_at = datetime.now()

    @abstractmethod
    def get_permissions(self) -> List[str]:
        pass


class Customer(User):
    """Customer class representing regular users."""

    def __init__(self, user_id: str, name: str, email: str, loyalty_points: int = 0):
        super().__init__(user_id, name, email)
        self.loyalty_points = loyalty_points
        self.orders: List['Order'] = []

    def get_permissions(self) -> List[str]:
        return ['view_products', 'place_order', 'view_own_orders']

    def add_order(self, order: 'Order'):
        self.orders.append(order)
        self.loyalty_points += order.get_total() // 10


class Admin(User):
    """Admin class with elevated permissions."""

    def get_permissions(self) -> List[str]:
        return [
            'view_products', 'place_order', 'view_all_orders',
            'manage_products', 'manage_users', 'view_analytics'
        ]


class Product:
    """Product class representing items for sale."""

    def __init__(self, product_id: str, name: str, price: float, category: str):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.stock_quantity = 0

    def update_stock(self, quantity: int):
        self.stock_quantity += quantity

    def is_available(self) -> bool:
        return self.stock_quantity > 0


class Order:
    """Order class representing customer orders."""

    def __init__(self, order_id: str, customer: Customer):
        self.order_id = order_id
        self.customer = customer
        self.items: List[OrderItem] = []
        self.status = "pending"
        self.created_at = datetime.now()

    def add_item(self, product: Product, quantity: int):
        if product.is_available() and quantity <= product.stock_quantity:
            item = OrderItem(product, quantity)
            self.items.append(item)
            product.update_stock(-quantity)
            return True
        return False

    def get_total(self) -> float:
        return sum(item.get_subtotal() for item in self.items)

    def mark_completed(self):
        self.status = "completed"


class OrderItem:
    """Order item representing a product in an order."""

    def __init__(self, product: Product, quantity: int):
        self.product = product
        self.quantity = quantity

    def get_subtotal(self) -> float:
        return self.product.price * self.quantity


class PaymentProcessor(ABC):
    """Abstract payment processor."""

    @abstractmethod
    def process_payment(self, amount: float) -> bool:
        pass


class CreditCardProcessor(PaymentProcessor):
    """Credit card payment processor."""

    def __init__(self, card_number: str, expiry_date: str):
        self.card_number = card_number
        self.expiry_date = expiry_date

    def process_payment(self, amount: float) -> bool:
        # Mock payment processing
        print(f"Processing credit card payment of ${amount}")
        return True


class PayPalProcessor(PaymentProcessor):
    """PayPal payment processor."""

    def __init__(self, email: str):
        self.email = email

    def process_payment(self, amount: float) -> bool:
        # Mock payment processing
        print(f"Processing PayPal payment of ${amount} for {self.email}")
        return True


class ECommerceSystem:
    """Main e-commerce system orchestrator."""

    def __init__(self):
        self.users: Dict[str, User] = {}
        self.products: Dict[str, Product] = {}
        self.orders: Dict[str, Order] = {}

    def register_customer(self, name: str, email: str) -> Customer:
        user_id = f"cust_{len(self.users) + 1}"
        customer = Customer(user_id, name, email)
        self.users[user_id] = customer
        return customer

    def register_admin(self, name: str, email: str) -> Admin:
        user_id = f"admin_{len(self.users) + 1}"
        admin = Admin(user_id, name, email)
        self.users[user_id] = admin
        return admin

    def add_product(self, product_id: str, name: str, price: float, category: str, stock: int):
        product = Product(product_id, name, price, category)
        product.update_stock(stock)
        self.products[product_id] = product

    def create_order(self, customer_id: str) -> Optional[Order]:
        customer = self.users.get(customer_id)
        if isinstance(customer, Customer):
            order_id = f"order_{len(self.orders) + 1}"
            order = Order(order_id, customer)
            self.orders[order_id] = order
            customer.add_order(order)
            return order
        return None

    def process_order(self, order_id: str, payment_processor: PaymentProcessor) -> bool:
        order = self.orders.get(order_id)
        if order and payment_processor.process_payment(order.get_total()):
            order.mark_completed()
            return True
        return False


def main():
    """Main function demonstrating the e-commerce system."""
    # Initialize system
    system = ECommerceSystem()

    # Add products
    system.add_product("p1", "Laptop", 999.99, "Electronics", 10)
    system.add_product("p2", "Mouse", 29.99, "Electronics", 50)
    system.add_product("p3", "Keyboard", 79.99, "Electronics", 30)

    # Register users
    customer = system.register_customer("John Doe", "john@example.com")
    admin = system.register_admin("Jane Smith", "jane@company.com")

    # Create and process order
    order = system.create_order(customer.user_id)
    if order:
        order.add_item(system.products["p1"], 1)
        order.add_item(system.products["p2"], 2)

        payment = CreditCardProcessor("4111111111111111", "12/25")
        success = system.process_order(order.order_id, payment)

        if success:
            print(f"Order {order.order_id} completed successfully!")
            print(f"Customer loyalty points: {customer.loyalty_points}")


if __name__ == "__main__":
    main()