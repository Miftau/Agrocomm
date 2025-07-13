from django.contrib import admin
from .models import Category, Farmer, Product, CartItem, Order, OrderItem

from django.contrib import admin
from .models import Category, Farmer, Product, CartItem, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ["name", "phone_number", "location", "is_approved", "created_at"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["name", "phone_number"]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock", "category", "farmer", "is_approved", "created_at"]
    list_filter = ["category", "is_approved"]
    search_fields = ["name"]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "product", "quantity", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["phone_number"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id", "phone_number", "total_amount", "payment_method",
        "payment_status", "transaction_reference", "status", "created_at"
    ]
    list_filter = ["payment_status", "payment_method", "status"]
    search_fields = ["phone_number", "transaction_reference"]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "price"]
    search_fields = ["product__name", "order__id"]


