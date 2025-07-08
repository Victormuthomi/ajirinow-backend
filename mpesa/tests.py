from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from payments.models import Payment
from django.utils import timezone
from unittest.mock import patch

class MpesaTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            phone_number="0711111111",
            name="Test Fundi",
            id_number="11111111",
            password="testpass123",
            role="fundi"
        )
        self.token = self.client.post(
            "/api/accounts/login/",
            {"phone_number": "0711111111", "password": "testpass123"},
        ).data["token"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

    @patch("mpesa.utils.lipa_na_mpesa_online")
    def test_stk_push_success(self, mock_lipa):
        mock_lipa.return_value = {
            "MerchantRequestID": "mocked_id",
            "CheckoutRequestID": "mocked_checkout",
            "ResponseCode": "0",
            "CustomerMessage": "STK push initiated"
        }

        response = self.client.post("/api/mpesa/stkpush/", {
            "purpose": "subscription",
            "phone": "0711111111"
        }, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("checkout_id", response.data)
        self.assertEqual(Payment.objects.count(), 1)

    def test_callback_success_subscription(self):
        payment = Payment.objects.create(
            user=self.user,
            phone="0711111111",
            amount=200,
            merchant_request_id="mocked_id",
            checkout_request_id="mocked_checkout",
            status="Pending",
            purpose="subscription"
        )

        data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "mocked_id",
                    "CheckoutRequestID": "mocked_checkout",
                    "ResultCode": 0,
                    "ResultDesc": "Success",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 200}
                        ]
                    }
                }
            }
        }

        response = self.client.post("/api/mpesa/callback/", data, format="json")
        self.assertEqual(response.status_code, 200)

        payment.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(payment.status, "Completed")
        self.assertEqual(self.user.subscription_end, timezone.now().date() + timezone.timedelta(days=30))

