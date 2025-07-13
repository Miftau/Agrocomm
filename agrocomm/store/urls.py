from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path("ussd/", ussd_callback, name="ussd_callback"),
    path("paystack/webhook/", views.paystack_webhook, name="paystack_webhook"),
    path("sms/status/", views.sms_delivery_report, name="sms_delivery_report"),
]
