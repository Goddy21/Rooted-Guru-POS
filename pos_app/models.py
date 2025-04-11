from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    # A one-to-one relationship with the User model.
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    designation = models.CharField(max_length=100, null=True, blank=True)  # Optional field for user's designation

    def __str__(self):
        return self.user.username  # Returns the username associated with the profile

class Product(models.Model):
    # Unique product code for each product.
    product_code = models.CharField(max_length=255)  # Added field for product code
    name = models.CharField(max_length=100)  # Product name
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price with two decimal places
    product_weight = models.CharField(max_length=100)  # Product weight
    description = models.TextField()  # Detailed product description
    stock_level = models.PositiveIntegerField(default=0)  # Tracks inventory levels of the product
    sales_count = models.PositiveIntegerField(default=0)  # Tracks the total sales of the product
    order_received = models.DateField(null=True, blank=True)  # Date when product was ordered
    last_purchase = models.DateField(null=True, blank=True)  # Date when the product was last purchased
    ordered = models.DateField(null=True, blank=True)  # Date when the product was last ordered

    def __str__(self):
        return self.name  # Returns the product's name as a string representation

    def update_sales_count(self, quantity_sold):
        """Method to update the sales count of a product."""
        self.sales_count += quantity_sold
        self.save()

    def update_stock_level(self, quantity_purchased):
        """Method to update the stock level after purchasing new stock."""
        self.stock_level += quantity_purchased
        self.save()

    def update_order_date(self):
        """Method to update the order date of the product."""
        self.order = self.ordered
        self.save()

    def update_last_purchase(self, purchase_date):
        """Method to update the last purchase date of the product."""
        self.last_purchase = purchase_date
        self.save()

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Reference to the User model
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')  # Set a custom related_name
    quantity = models.PositiveIntegerField(default=1)  # Number of products in the order
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Total price for the order
    order_date = models.DateField(auto_now_add=True)  # Date when the order was placed

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def calculate_total_price(self):
        """Method to calculate total price of the order."""
        self.total_price = self.quantity * self.product.price
        self.save()
