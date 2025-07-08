from django.contrib import admin
from .models import Category, Farmer, Product, CartItem, Order, OrderItem

admin.site.register(Category)
admin.site.register(Farmer)
admin.site.register(Product)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "phone_number", "total_amount", "payment_status", "payment_method", "transaction_reference"]
    list_filter = ["payment_status", "payment_method"]
    search_fields = ["phone_number", "transaction_reference"]

