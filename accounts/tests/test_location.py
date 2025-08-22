from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User, EmailOTP

class LocationTests(APITestCase):

    def setUp(self):
        self.user_data = {
            "email": "client@example.com",
            "full_name": "Client User",
            "password": "password123",
            "role": "client",
            "country": "Rwanda",
            "state": "",
            "city": "Kigali",
            "street_address": "KG 123 St"
        }
        self.client.post(reverse("accounts:register"), self.user_data, format='json')
        self.user = User.objects.get(email="client@example.com")
        otp_obj = EmailOTP.create_otp(self.user)
        response = self.client.post(reverse("accounts:verify-otp"), {"email": self.user.email, "otp": otp_obj.otp}, format='json')
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_get_location(self):
        url = reverse("accounts:user-location")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["city"], "Kigali")

    def test_update_location(self):
        url = reverse("accounts:user-location")
        new_data = {"city": "Huye", "street_address": "New Address 456"}
        response = self.client.put(url, new_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["city"], "Huye")
        self.assertEqual(response.data["street_address"], "New Address 456")
