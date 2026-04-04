import os

APP_NAME = "Vanya Raksha AI"
DB_PATH = "app.db"

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
TWILIO_SMS_FROM = os.getenv("TWILIO_SMS_FROM", "")
