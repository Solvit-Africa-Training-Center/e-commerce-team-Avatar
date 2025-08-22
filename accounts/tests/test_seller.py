from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User, EmailOTP

class SellerProfileTests(APITestCase):

    def setUp(self):
        self.seller_data = {
            "email": "seller@example.com",
            "full_name": "Seller User",
            "password": "password123",
            "role": "seller",
            "country": "Rwanda",
            "state": "",
            "city": "Kigali",
            "street_address": "KG 456 St"
        }
        self.client.post(reverse("accounts:register"), self.seller_data, format='json')
        self.user = User.objects.get(email="seller@example.com")
        otp_obj = EmailOTP.create_otp(self.user)
        response = self.client.post(reverse("accounts:verify-otp"), {"email": self.user.email, "otp": otp_obj.otp}, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_get_seller_profile(self):
        url = reverse("accounts:seller-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["store_name"], "Seller User's Store")

    def test_update_seller_profile(self):
        url = reverse("accounts:seller-profile")
        new_data = {"store_name": "Updated Store Name"}
        response = self.client.put(url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["store_name"], "Updated Store Name")

    def test_non_seller_cannot_access_profile(self):
        # Register a client user
        client_data = {
            "email": "client@example.com",
            "full_name": "Client User",
            "password": "password123",
            "role": "client",
            "country": "Rwanda",
            "state": "",
            "city": "Kigali",
            "street_address": "KG 123 St"
        }
        self.client.post(reverse("accounts:register"), client_data, format='json')
        user = User.objects.get(email="client@example.com")
        otp_obj = EmailOTP.create_otp(user)
        response = self.client.post(reverse("accounts:verify-otp"), {"email": user.email, "otp": otp_obj.otp}, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        url = reverse("accounts:seller-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
