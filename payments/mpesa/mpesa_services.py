from django.conf import settings
import requests
import json

class MpesaService:
    def __init__(self):
        self.base_url = settings.MPESA_BASE_URL
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.lipa_na_mpesa_online_shortcode = settings.LIPA_NA_MPESA_ONLINE_SHORTCODE
        self.lipa_na_mpesa_online_shortcode_key = settings.LIPA_NA_MPESA_ONLINE_SHORTCODE_KEY
        self.lipa_na_mpesa_online_shortcode_passkey = settings.LIPA_NA_MPESA_ONLINE_SHORTCODE_PASSKEY

    def get_access_token(self):
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
        json_response = response.json()
        return json_response['access_token']

    def initiate_payment(self, amount, phone_number):
        access_token = self.get_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            "BusinessShortCode": self.lipa_na_mpesa_online_shortcode,
            "Password": self.lipa_na_mpesa_online_shortcode_passkey,
            "Timestamp": self.get_timestamp(),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.lipa_na_mpesa_online_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": f"{settings.CALLBACK_URL}/mpesa/callbacks/",
            "AccountReference": "Test123",
            "TransactionDesc": "Payment for testing"
        }
        response = requests.post(f"{self.base_url}/mpesa/stkpush/v1/processrequest", headers=headers, json=payload)
        # return response.json()
        return MpesaService().initiate_payment(amount, phone_number)

    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d%H%M%S')