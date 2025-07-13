from django.contrib import admin
from store.models import Farmer, Product, Order, OrderItem


@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "location", "is_approved")
    list_filter = ("is_approved",)
    search_fields = ("name", "phone_number", "location")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "farmer", "price", "stock", "is_approved")
    list_filter = ("is_approved",)
    search_fields = ("name", "farmer__name")
    autocomplete_fields = ["farmer"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "customer_phone", "status", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("customer_name", "customer_phone", "id")
    inlines = [OrderItemInline]
    readonly_fields = ("total_amount",)

