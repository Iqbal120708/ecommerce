# from rest_framework.test import APITestCase
from unittest.mock import patch

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


class UserDetailTest(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test",
            email="test@gmail.com",
            password="test2938484jr",
            phone_number="089384442947",
        )
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True, primary=True
        )

    @patch("accounts.signals.logger")
    def test_success(self, mock_logger):
        login = self.client.post(
            reverse("rest_login"),
            {"email": self.user.email, "password": "test2938484jr"},
            format="json",
        )

        self.assertEqual(login.status_code, 200)

        token = login.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response_user = self.client.get(reverse("rest_user_details"))

        self.assertEqual(response_user.status_code, 200)

        self.assertEqual(response_user.data["id"], 1)
        self.assertEqual(response_user.data["first_name"], "")
        self.assertEqual(response_user.data["last_name"], "")
        self.assertEqual(response_user.data["username"], "test")
        self.assertEqual(response_user.data["email"], "test@gmail.com")
        self.assertEqual(response_user.data["phone_number"], "+6289384442947")
        self.assertEqual(response_user.data["shipping_addresses"], [])
