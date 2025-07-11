import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def send_sms(to_number: str, body: str):
    """
    Sends an SMS using Twilio credentials from environment variables.
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    twilio_phone_number = os.environ.get("TWILIO_PHONE_NUMBER")

    if not all([account_sid, auth_token, twilio_phone_number]):
        print("Twilio credentials (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, or TWILIO_PHONE_NUMBER) are not set in the .env file.")
        return

    client = Client(account_sid, auth_token)
    try:
        if not to_number.startswith('+'):
            to_number = f"+91{to_number.strip()}"

        message = client.messages.create(body=body, from_=twilio_phone_number, to=to_number)
        print(f"SMS sent to {to_number}: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS to {to_number}: {e}")