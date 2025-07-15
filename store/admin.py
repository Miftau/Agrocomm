from django.contrib import admin
from .models import Category, Farmer, Product, CartItem, Order, OrderItem
from django import forms
from django.shortcuts import render, redirect
import csv
from io import TextIOWrapper
from django.contrib import messages

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ["name", "phone_number", "location", "is_approved", "created_at"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["name", "phone_number"]

class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stock", "category", "farmer", "is_approved", "created_at"]
    list_filter = ["category", "is_approved"]
    search_fields = ["name"]


    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.upload_csv)
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = TextIOWrapper(request.FILES["csv_upload"].file, encoding='utf-8')
            reader = csv.DictReader(csv_file)

            for row in reader:
                try:
                    category = Category.objects.get(name=row['category'])
                    farmer = Farmer.objects.get(phone_number=row['farmer_phone'])

                    Product.objects.create(
                        name=row['name'],
                        price=float(row['price']),
                        stock=int(row['stock']),
                        category=category,
                        farmer=farmer,
                        is_approved=True
                    )
                except Exception as e:
                    messages.error(request, f"Error: {e}")
                    continue

            self.message_user(request, "Products uploaded successfully.")
            return redirect("..")

        form = CsvImportForm()
        return render(request, "admin/csv_form.html", {"form": form})

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


