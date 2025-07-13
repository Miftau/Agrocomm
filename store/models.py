import datetime
from django.utils import timezone

from django.db import models
from django.views.generic.dates import timezone_today


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Farmer(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    location = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return f"{self.name} ({self.phone_number})"


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    session_id = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"


class Order(models.Model):
    phone_number = models.CharField(max_length=15)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=30, choices=[
        ("Unpaid", "Unpaid"),
        ("Pending", "Pending"),
        ("Awaiting Confirmation", "Awaiting Confirmation"),
        ("Paid", "Paid"),
        ("Failed", "Failed"),
        ("Pay on Delivery", "Pay on Delivery")
    ], default="Unpaid")
    payment_method = models.CharField(max_length=20, choices=[
        ("Paystack", "Paystack"),
        ("Bank Transfer", "Bank Transfer"),
        ("Pay on Delivery", "Pay on Delivery")
    ], default="Bank Transfer")
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered")
    ], default="Processing")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.price

