from twilio.rest import Client
from dotenv import load_dotenv
import os

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
from_number = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(account_sid, auth_token)

def send_whatsapp_message(message):

    recipients = os.getenv("RECIPIENTS", "")
    recipients = [x.strip() for x in recipients.split(",") if x.strip()]

    for recipient in recipients:

        try:

            response = client.messages.create(
                body=message,
                from_=from_number,
                to=recipient
            )

            print(f"SUCCESS: {response.sid}")

        except Exception as e:

            print(f"FAILED: {e}")