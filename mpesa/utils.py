import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings
from datetime import datetime
import base64


def get_access_token():
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        url,
        auth=HTTPBasicAuth(
            settings.MPESA_CONSUMER_KEY,
            settings.MPESA_CONSUMER_SECRET
        )
    )

    print("🔑 Access Token Response:", response.status_code, response.text)  # TEMP: for debugging

    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.text}")

    token = response.json().get("access_token")
    if not token:
        raise Exception("No access token returned.")
    return token


def lipa_na_mpesa_online(phone_number, amount):
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    password_str = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    password = base64.b64encode(password_str.encode()).decode()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.CALLBACK_URL,
        "AccountReference": "AjiriNow",
        "TransactionDesc": "Subscription"
    }

    print("📦 STK Payload:", payload)  # TEMP: for debugging

    response = requests.post(
        f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest",
        headers=headers,
        json=payload
    )

    print("📲 STK Push Response:", response.status_code, response.text)  # TEMP: for debugging

    if response.status_code != 200:
        raise Exception(f"STK Push failed: {response.text}")

    return response.json()

