from django.conf import settings
import requests
import base64
import time

class DarajaClient:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.lipa_na_mpesa_online_shortcode = settings.MPESA_LIPA_NA_MPESA_ONLINE_SHORTCODE
        self.lipa_na_mpesa_online_shortcode_key = settings.MPESA_LIPA_NA_MPESA_ONLINE_SHORTCODE_KEY
        self.api_url = "https://sandbox.safaricom.co.ke"
        self.token = None

    def generate_token(self):
        api_url = f"{self.api_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(api_url, auth=(self.consumer_key, self.consumer_secret))
        if response.status_code == 200:
            json_response = response.json()
            self.token = json_response['access_token']
            return self.token
        else:
            raise Exception("Failed to generate token")

    def lipa_na_mpesa_online(self, amount, phone_number):
        if not self.token:
            self.generate_token()

        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "BusinessShortCode": self.lipa_na_mpesa_online_shortcode,
            "Password": self._generate_password(),
            "Timestamp": self._generate_timestamp(),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.lipa_na_mpesa_online_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": "Test123",
            "TransactionDesc": "Payment for testing"
        }

        response = requests.post(f"{self.api_url}/mpesa/paymentrequest", json=payload, headers=headers)
        return response.json()

    def _generate_password(self):
        return base64.b64encode(f"{self.lipa_na_mpesa_online_shortcode}{self.lipa_na_mpesa_online_shortcode_key}{self._generate_timestamp()}".encode()).decode()

    def _generate_timestamp(self):
        return time.strftime('%Y%m%d%H%M%S', time.gmtime())