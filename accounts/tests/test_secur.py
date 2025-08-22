from datetime import timedelta
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User, EmailOTP

class AuthTests(APITestCase):

    def setUp(self):
        self.client_user_data = {
            "email": "client@example.com",
            "full_name": "Client User",
            "password": "password123",
            "role": "client",
            "country": "Rwanda",
            "state": "",
            "city": "Kigali",
            "street_address": "KG 123 St"
        }
        self.seller_user_data = {
            "email": "seller@example.com",
            "full_name": "Seller User",
            "password": "password123",
            "role": "seller",
            "country": "Rwanda",
            "state": "",
            "city": "Kigali",
            "street_address": "KG 456 St"
        }

    # Registration tests
    def test_register_client_user(self):
        response = self.client.post(reverse("accounts:register"), self.client_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="client@example.com").exists())

    def test_register_seller_creates_seller_profile(self):
        response = self.client.post(reverse("accounts:register"), self.seller_user_data, format='json')
        user = User.objects.get(email="seller@example.com")
        self.assertTrue(hasattr(user, "seller_profile"))

    def test_register_duplicate_email_fails(self):
        self.client.post(reverse("accounts:register"), self.client_user_data, format='json')
        response = self.client.post(reverse("accounts:register"), self.client_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # OTP tests
    def test_verify_otp_success(self):
        self.client.post(reverse("accounts:register"), self.client_user_data, format='json')
        user = User.objects.get(email="client@example.com")
        otp_obj = EmailOTP.create_otp(user)
        data = {"email": user.email, "otp": otp_obj.otp}
        response = self.client.post(reverse("accounts:verify-otp"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_verify_invalid_otp(self):
        data = {"email": "nonexistent@example.com", "otp": "123456"}
        response = self.client.post(reverse("accounts:verify-otp"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verify_expired_otp(self):
        self.client.post(reverse("accounts:register"), self.client_user_data, format='json')
        user = User.objects.get(email="client@example.com")
        otp_obj = EmailOTP.create_otp(user)
        otp_obj.expires_at -= timedelta(minutes=10)
        otp_obj.save()
        data = {"email": user.email, "otp": otp_obj.otp}
        response = self.client.post(reverse("accounts:verify-otp"), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
