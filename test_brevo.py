import os
import requests
from dotenv import load_dotenv

load_dotenv('.env')

api_key = os.getenv('VITE_BREVO_API_KEY')
sender_email = os.getenv('VITE_SENDER_EMAIL')

headers = {
    'accept': 'application/json',
    'api-key': api_key,
    'content-type': 'application/json'
}
data = {
    "sender": {"email": sender_email, "name": "Netiacademy"},
    "to": [{"email": "satya@admin.com", "name": "Satya"}],
    "subject": "Netiacademy - Password Reset",
    "htmlContent": "<html><body><p>Test email</p></body></html>"
}

try:
    response = requests.post('https://api.brevo.com/v3/smtp/email', headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
