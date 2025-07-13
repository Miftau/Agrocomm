from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Admin dashboard
    path('', views.dashboard, name='admin_dashboard'),

    # Authentication
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),

    # Farmer views
    path('farmers/', views.farmer_list, name='farmer_list'),
    path('approve/farmer/<int:farmer_id>/', views.approve_farmer, name='approve_farmer'),

    # Product views
    path('products/', views.product_list, name='product_list'),
    path('approve/product/<int:product_id>/', views.approve_product, name='approve_product'),
    path('delete/product/<int:product_id>/', views.delete_product, name='delete_product'),

    # Order views
    path('orders/', views.order_list, name='order_list'),

    # CSV bulk upload
    path('upload/products/', views.upload_products_csv, name='upload_products_csv'),

    # Export paths
    path('export/orders/', views.export_orders_csv, name='export_orders_csv'),
    path('export/products/', views.export_products_csv, name='export_products_csv'),
    path('export/farmers/', views.export_farmers_csv, name='export_farmers_csv'),

]
