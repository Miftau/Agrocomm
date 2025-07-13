from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Farmer, Product, CartItem, Order, OrderItem, Category
from store.utils.paystack import initialize_payment
from store.utils.sms import send_sms
import json

@csrf_exempt
def ussd_callback(request):
    if request.method != 'POST':
        return HttpResponse("END Invalid method", content_type="text/plain")

    session_id = request.POST.get("sessionId", "")
    phone_number = request.POST.get("phoneNumber", "")
    text = request.POST.get("text", "").strip()
    inputs = text.split("*")

    response = ""

    if text == "":
        response = (
            "CON Welcome to Agrocomm\n"
            "1. Shop\n"
            "2. My Cart\n"
            "3. Register as Farmer\n"
            "4. Add Produce\n"
            "5. My Orders\n"
            "6. Help"
        )

    # SHOP
    elif inputs[0] == "1":
        if len(inputs) == 1:
            categories = Category.objects.all()
            if not categories.exists():
                return HttpResponse("END No categories found.", content_type="text/plain")
            response = "CON Select Category:\n"
            for i, cat in enumerate(categories, 1):
                response += f"{i}. {cat.name}\n"
        elif len(inputs) == 2:
            cat_index = int(inputs[1]) - 1
            categories = list(Category.objects.all())
            if cat_index < 0 or cat_index >= len(categories):
                return HttpResponse("END Invalid category selected.", content_type="text/plain")
            selected_category = categories[cat_index]
            products = Product.objects.filter(category=selected_category, is_approved=True)
            if not products.exists():
                return HttpResponse("END No products in this category.", content_type="text/plain")
            response = "CON Select Product:\n"
            for i, prod in enumerate(products, 1):
                response += f"{i}. {prod.name} - \u20a6{prod.price}\n"
        elif len(inputs) == 3:
            response = "CON Enter quantity:"
        elif len(inputs) == 4:
            try:
                cat_index = int(inputs[1]) - 1
                prod_index = int(inputs[2]) - 1
                quantity = int(inputs[3])
                category = list(Category.objects.all())[cat_index]
                product = list(Product.objects.filter(category=category, is_approved=True))[prod_index]
                CartItem.objects.create(
                    session_id=session_id,
                    phone_number=phone_number,
                    product=product,
                    quantity=quantity
                )
                response = "CON Added to cart!\n1. Add more\n2. Exit"
            except:
                response = "END Error adding to cart."
        elif len(inputs) == 5:
            if inputs[4] == "1":
                categories = Category.objects.all()
                response = "CON Select Category:\n"
                for i, cat in enumerate(categories, 1):
                    response += f"{i}. {cat.name}\n"
            else:
                response = "END Thanks for shopping. View cart to checkout."

    # MY CART + ORDER
    elif inputs[0] == "2":
        cart_items = CartItem.objects.filter(phone_number=phone_number)
        if len(inputs) == 1:
            if not cart_items.exists():
                response = "END Cart is empty."
            else:
                total = 0
                response = "CON Cart:\n"
                for item in cart_items:
                    amount = item.product.price * item.quantity
                    total += amount
                    response += f"{item.product.name} x{item.quantity} = \u20a6{amount}\n"
                response += f"\nTotal: \u20a6{total}\n1. Proceed to Payment\n2. Cancel"

        elif len(inputs) == 2 and inputs[1] == "1":
            response = (
                "CON Choose Payment Option:\n"
                "1. Paystack (online)\n"
                "2. Bank Transfer\n"
                "3. Pay on Delivery"
            )

        elif len(inputs) == 3:
            payment_option = inputs[2]
            total = sum(item.product.price * item.quantity for item in cart_items)
            payment_method = ""

            if payment_option == "1":
                payment_method = "Paystack"
            elif payment_option == "2":
                payment_method = "Bank Transfer"
            elif payment_option == "3":
                payment_method = "Pay on Delivery"
            else:
                return HttpResponse("END Invalid payment option selected.", content_type="text/plain")

            order = Order.objects.create(
                phone_number=phone_number,
                total_amount=total,
                payment_status="Pending" if payment_method != "Pay on Delivery" else "Pay on Delivery",
                payment_method=payment_method
            )

            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
                item.product.stock -= item.quantity
                item.product.save()
            cart_items.delete()

            if payment_option == "1":
                email = f"user_{phone_number}@agrocomm.com"
                result = initialize_payment(email, total, order.id)
                if result.get("status") and result.get("data"):
                    pay_url = result["data"]["authorization_url"]
                    send_sms(phone_number, f"Pay for your Agrocomm order: {pay_url}")
                    response = "END Order placed. Payment link sent via SMS."
                else:
                    order.payment_status = "Failed"
                    order.save()
                    response = "END Payment initialization failed."

            elif payment_option == "2":
                send_sms(phone_number, f"Transfer \u20a6{total} to Agrocomm Account:\nGTBank 1234567890.\nUse your phone number as reference.")
                response = "END Order placed. Bank transfer instructions sent via SMS."

            elif payment_option == "3":
                response = "END Order placed. You will pay upon delivery."

        elif len(inputs) == 2 and inputs[1] == "2":
            cart_items.delete()
            response = "END Cart cleared."

    # REGISTER FARMER
    elif inputs[0] == "3":
        if len(inputs) == 1:
            response = "CON Enter your full name:"
        elif len(inputs) == 2:
            response = "CON Enter your farm location:"
        elif len(inputs) == 3:
            name = inputs[1]
            location = inputs[2]
            if Farmer.objects.filter(phone_number=phone_number).exists():
                response = "END Already registered. Await approval."
            else:
                Farmer.objects.create(name=name, phone_number=phone_number, location=location, is_approved=False)
                response = "END Thank you. Await admin approval."

    # ADD PRODUCE
    elif inputs[0] == "4":
        try:
            farmer = Farmer.objects.get(phone_number=phone_number, is_approved=True)
        except Farmer.DoesNotExist:
            return HttpResponse("END Only approved farmers can add produce.", content_type="text/plain")
        if len(inputs) == 1:
            response = "CON Enter product name:"
        elif len(inputs) == 2:
            response = "CON Enter price:"
        elif len(inputs) == 3:
            response = "CON Enter quantity:"
        elif len(inputs) == 4:
            categories = Category.objects.all()
            response = "CON Select category:\n"
            for i, cat in enumerate(categories, 1):
                response += f"{i}. {cat.name}\n"
        elif len(inputs) == 5:
            try:
                name = inputs[1]
                price = float(inputs[2])
                quantity = int(inputs[3])
                category_index = int(inputs[4]) - 1
                category = list(Category.objects.all())[category_index]

                Product.objects.create(
                    name=name,
                    price=price,
                    stock=quantity,
                    category=category,
                    farmer=farmer,
                    is_approved=False
                )
                response = "END Product added. Await admin approval."
            except (IndexError, ValueError) as e:
                response = "END Invalid input values."
            except Exception as e:
                print("USSD Add Produce Error:", str(e))  # Optional: log to file
                response = "END Failed to add product. Please try again."


    # MY ORDERS + TRACKING
    elif inputs[0] == "5":
        orders = Order.objects.filter(phone_number=phone_number).order_by('-created_at')[:5]
        if len(inputs) == 1:
            if not orders.exists():
                response = "END No orders yet."
            else:
                response = "CON Select order to track:\n"
                for i, order in enumerate(orders, 1):
                    response += f"{i}. Order #{order.id} - \u20a6{order.total_amount}\n"
        elif len(inputs) == 2:
            try:
                order = list(orders)[int(inputs[1]) - 1]
                response = f"END Order #{order.id} status: {order.status} ({order.payment_status})"
            except:
                response = "END Invalid selection."

    elif inputs[0] == "6":
        response = (
            "END Help:\n"
            "- 1: Shop\n"
            "- 2: View Cart\n"
            "- 3: Farmer Reg\n"
            "- 4: Add Produce\n"
            "- 5: Track Orders"
        )

    else:
        response = "END Invalid input."

    return HttpResponse(response, content_type="text/plain")


@csrf_exempt
def paystack_webhook(request):
    payload = json.loads(request.body.decode('utf-8'))
    event = payload.get("event")
    if event == "charge.success":
        order_id = payload["data"]["metadata"].get("order_id")
        try:
            order = Order.objects.get(id=order_id)
            order.payment_status = "Paid"
            order.save()
        except Order.DoesNotExist:
            pass
    return HttpResponse(status=200)

@csrf_exempt
def sms_delivery_report(request):
    if request.method == 'POST':
        phone_number = request.POST.get("phoneNumber")
        status = request.POST.get("status")
        message_id = request.POST.get("messageId")
        cost = request.POST.get("cost")

        print(f"SMS to {phone_number} - Status: {status} - Cost: {cost}")
        # Optionally save status in DB
        return HttpResponse("OK")
    return HttpResponse("Invalid Method")

