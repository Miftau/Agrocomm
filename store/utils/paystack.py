import requests
from django.conf import settings

def initialize_payment(email, amount, order_id):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "amount": int(amount * 100),  # Convert to kobo
        "metadata": {
            "order_id": order_id
        },
        "callback_url": f"{settings.YOUR_DOMAIN}/paystack/verify/"
    }

    response = requests.post(url, json=data, headers=headers)
    return response.json()

