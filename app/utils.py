import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def send_sms(to_number: str, body: str):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not account_sid or not auth_token:
        print("Twilio credentials not set")
        return
    client = Client(account_sid, auth_token)
    try:
        message = client.messages.create(
            body=body,
            from_="+12513136336",
            # to=f"+91{to_number}",  # Uncomment this line if you want to use the dynamic number
            to="+919306374883"
        )
        print(f"SMS sent to {to_number}: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")