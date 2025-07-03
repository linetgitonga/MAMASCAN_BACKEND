from django.conf import settings
import hashlib
import random
import string
import requests
import json

def generate_payment_link(amount, service_id):
    """Generates a unique payment link for a given amount and service."""
    unique_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    payment_link = f"{settings.PAYMENT_GATEWAY_URL}/pay?amount={amount}&service_id={service_id}&id={unique_id}"
    return payment_link

def validate_payment_response(response):
    """Validates the payment response from the payment gateway."""
    expected_signature = hashlib.sha256((response['amount'] + response['status'] + settings.SECRET_KEY).encode()).hexdigest()
    return expected_signature == response['signature']

def format_currency(amount):
    """Formats the amount to a currency string."""
    return f"${amount:.2f}"

def initiate_mpesa_payment(amount, phone_number, service_id):
    """Initiates a payment through M-Pesa."""
    url = f"{settings.MPESA_API_URL}/payment/request"
    headers = {
        "Authorization": f"Bearer {get_mpesa_access_token()}",
        "Content-Type": "application/json"
    }
    payload = {
        "amount": amount,
        "phone_number": phone_number,
        "service_id": service_id
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def get_mpesa_access_token():
    """Retrieves the access token for M-Pesa API."""
    url = f"{settings.MPESA_API_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    return response.json().get('access_token')