from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
import csv
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Q
from store.models import Farmer, Product, Order


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid credentials or not an admin user.")
    return render(request, "adminpanel/login.html")


@login_required
def admin_logout(request):
    logout(request)
    return redirect("admin_login")




def get_range_bounds(ranges):
    now = timezone.now()
    if ranges == "week":
        current_start = now - timedelta(days=7)
        previous_start = current_start - timedelta(days=7)
    elif ranges == "month":
        current_start = now - timedelta(days=30)
        previous_start = current_start - timedelta(days=30)
    else:
        current_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        previous_start = current_start - timedelta(days=1)
    return current_start, previous_start

# =============================
# ADMIN DASHBOARD OVERVIEW
# =============================
@login_required
def dashboard(request):
    ranges = request.GET.get("range", "day")
    current_start, previous_start = get_range_bounds(ranges)

    # KPI counters
    approved_farmers = Farmer.objects.filter(is_approved=True).count()
    pending_farmers = Farmer.objects.filter(is_approved=False).count()
    total_orders = Order.objects.count()
    out_of_stock = Product.objects.filter(stock__lte=0).count()

    current_farmers = Farmer.objects.filter(created_at__gte=current_start).count()
    current_orders = Order.objects.filter(created_at__gte=current_start).count()
    current_products = Product.objects.filter(created_at__gte=current_start).count()

    previous_farmers = Farmer.objects.filter(created_at__gte=previous_start, created_at__lt=current_start).count()
    previous_orders = Order.objects.filter(created_at__gte=previous_start, created_at__lt=current_start).count()
    previous_products = Product.objects.filter(created_at__gte=previous_start, created_at__lt=current_start).count()

    def get_growth(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100, 1)

    chart_data = {
        "farmers": [approved_farmers, pending_farmers],
        "products": [
            Product.objects.filter(is_approved=True).count(),
            Product.objects.filter(is_approved=False).count(),
            out_of_stock,
        ],
        "orders": [
            Order.objects.filter(status="Pending").count(),
            Order.objects.filter(status="Delivered").count(),
            Order.objects.filter(status="Cancelled").count(),
        ],
        "payments": [
            Order.objects.filter(payment_method="Paystack").count(),
            Order.objects.filter(payment_method="Bank Transfer").count(),
            Order.objects.filter(payment_method="Pay on Delivery").count(),
        ],
    }

    return render(request, "adminpanel/dashboard.html", {
        "range": range,
        "approved_farmers": approved_farmers,
        "pending_farmers": pending_farmers,
        "total_orders": total_orders,
        "out_of_stock": out_of_stock,
        "new_farmers": current_farmers,
        "new_orders": current_orders,
        "new_products": current_products,
        "growth_farmers": get_growth(current_farmers, previous_farmers),
        "growth_orders": get_growth(current_orders, previous_orders),
        "growth_products": get_growth(current_products, previous_products),
        "chart_data": chart_data,
    })

# =============================
# FARMER VIEWS
# =============================
@login_required
def farmer_list(request):
    query = request.GET.get("q")
    farmers = Farmer.objects.all()
    if query:
        farmers = farmers.filter(name__icontains=query)
    return render(request, "adminpanel/farmers.html", {"farmers": farmers, "query": query})

@login_required
def approve_farmer(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    farmer.is_approved = True
    farmer.save()
    return redirect("farmer_list")


# =============================
# PRODUCT VIEWS
# =============================
@login_required
def product_list(request):
    products = Product.objects.all()
    query = request.GET.get("q")
    status = request.GET.get("status")

    if query:
        products = products.filter(name__icontains=query)

    if status == "approved":
        products = products.filter(is_approved=True)
    elif status == "pending":
        products = products.filter(is_approved=False)
    elif status == "outofstock":
        products = products.filter(stock=0)

    return render(request, "adminpanel/products.html", {
        "products": products,
        "query": query,
        "status": status,
    })

@login_required
def approve_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_approved = True
    product.save()
    return redirect("product_list")

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect("product_list")


# =============================
# ORDER VIEWS
# =============================
@login_required
def order_list(request):
    orders = Order.objects.select_related().all()
    query = request.GET.get("q")
    status = request.GET.get("status")

    if query:
        orders = orders.filter(id__icontains=query)

    if status:
        orders = orders.filter(status=status)

    return render(request, "adminpanel/orders.html", {
        "orders": orders,
        "query": query,
        "status": status,
    })


# =============================
# CSV BULK UPLOAD
# =============================
@login_required
def upload_products_csv(request):
    if request.method == "POST" and request.FILES.get("csv_file"):
        csv_file = request.FILES["csv_file"]

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "Please upload a CSV file.")
            return HttpResponseRedirect(reverse("upload_products_csv"))

        file_data = csv_file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(file_data)

        count = 0
        for row in reader:
            try:
                farmer = Farmer.objects.get(phone_number=row["farmer_phone"])
                Product.objects.create(
                    name=row["name"],
                    description=row.get("description", ""),
                    price=row.get("price", 0),
                    stock=row.get("stock", 0),
                    farmer=farmer,
                    is_approved=row.get("is_approved", "False").lower() == "true",
                )
                count += 1
            except Farmer.DoesNotExist:
                messages.warning(request, f"Farmer not found: {row['farmer_phone']}")
                continue
            except Exception as e:
                messages.error(request, f"Error: {e}")
                continue

        messages.success(request, f"{count} products uploaded successfully.")
        return HttpResponseRedirect(reverse("product_list"))

    return render(request, "adminpanel/upload_products.html")

import csv
from django.http import HttpResponse


@login_required
def export_orders_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer Name', 'Phone', 'Status', 'Payment', 'Amount', 'Created'])

    for order in Order.objects.all():
        writer.writerow([order.id, order.customer_name, order.customer_phone, order.status,
                         order.payment_method, order.total_amount, order.created_at])
    return response


@login_required
def export_products_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)
    writer.writerow(['Product Name', 'Farmer', 'Price', 'Stock', 'Approved'])

    for product in Product.objects.select_related('farmer').all():
        writer.writerow([product.name, product.farmer.name, product.price, product.stock, product.is_approved])
    return response


@login_required
def export_farmers_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="farmers.csv"'
    writer = csv.writer(response)
    writer.writerow(['Farmer Name', 'Phone', 'Location', 'Approved'])

    for farmer in Farmer.objects.all():
        writer.writerow([farmer.name, farmer.phone_number, farmer.location, farmer.is_approved])
    return response
