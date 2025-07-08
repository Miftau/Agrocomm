from africastalking.SMS import SMSService
from django.conf import settings

# Initialize Africa's Talking
SMSService(
    username=settings.AFRICASTALKING_USERNAME,
    api_key=settings.AFRICASTALKING_API_KEY
)

sms = SMSService

def send_sms(to_number, message):
    try:
        response = sms.send(message, [to_number])
        return response
    except Exception as e:
        print(f"SMS sending failed: {e}")
        return {"error": str(e)}