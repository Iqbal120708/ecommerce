# from rest_framework.test import APITestCase
from datetime import timedelta
from unittest.mock import patch

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.urls import reverse
from freezegun import freeze_time
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class LogRefreshTest(TransactionTestCase):
    reset_sequences = True
    client = APIClient()

    def setUp(self):
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
    @patch("accounts.log_utils.logger")
    def test_success(self, mock_logger1, mock_logger2):
        login = self.client.post(
            reverse("rest_login"),
            {"email": self.user.email, "password": "test2938484jr"},
            format="json",
        )

        self.assertEqual(login.status_code, 200)

        # lakukan request refresh token
        refresh = self.client.post(reverse("token_refresh"))

        mock_logger1.info.assert_called()

        args, kwargs = mock_logger1.info.call_args

        self.assertEqual(args[0], "refresh token success")
        self.assertEqual(kwargs["extra"]["event_type"], "token_refresh")
        self.assertEqual(kwargs["extra"]["user_id"], 1)
        self.assertEqual(kwargs["extra"]["status"], "success")

    @freeze_time("2025-12-01")
    @patch("accounts.signals.logger")
    @patch("accounts.log_utils.logger")
    def test_expired_token(self, mock_logger1, mock_logger2):
        login = self.client.post(
            reverse("rest_login"),
            {"email": self.user.email, "password": "test2938484jr"},
            format="json",
        )

        self.assertEqual(login.status_code, 200)

        with freeze_time("2025-12-10"):
            # lakukan request refresh token
            response = self.client.post(reverse("token_refresh"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Token is expired")

        mock_logger1.warning.assert_called()

        args, kwargs = mock_logger1.warning.call_args

        self.assertEqual(args[0], "Token is expired")
        self.assertEqual(kwargs["extra"]["event_type"], "token_refresh")
        self.assertEqual(kwargs["extra"]["user_id"], 1)
        self.assertEqual(kwargs["extra"]["status"], "failure")

    @patch("accounts.signals.logger")
    @patch("accounts.log_utils.logger")
    def test_blacklisted_token(self, mock_logger1, mock_logger2):
        login = self.client.post(
            reverse("rest_login"),
            {"email": self.user.email, "password": "test2938484jr"},
            format="json",
        )

        self.assertEqual(login.status_code, 200)

        refresh_cookie = self.client.cookies.get("_refresh_token")
        self.assertIsNotNone(refresh_cookie)

        token_str = refresh_cookie.value  # token string murni

        # Blacklist refresh token yang sama
        refresh = RefreshToken(token_str)
        refresh.blacklist()

        # lakukan request refresh token
        response = self.client.post(reverse("token_refresh"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Token is blacklisted")

        mock_logger1.warning.assert_called()

        args, kwargs = mock_logger1.warning.call_args

        self.assertEqual(args[0], "Token is blacklisted")
        self.assertEqual(kwargs["extra"]["event_type"], "token_refresh")
        self.assertEqual(kwargs["extra"]["user_id"], 1)
        self.assertEqual(kwargs["extra"]["status"], "failure")

    @patch("accounts.signals.logger")
    @patch("accounts.log_utils.logger")
    def test_corrupted_refresh_cookie(self, mock_logger1, mock_logger2):
        login = self.client.post(
            reverse("rest_login"),
            {"email": self.user.email, "password": "test2938484jr"},
            format="json",
        )

        self.assertEqual(login.status_code, 200)

        # Buat token refresh asli
        refresh = RefreshToken.for_user(self.user)
        refresh_str = str(refresh)

        # Buat token corrupt
        bad = refresh_str[:-3] + "xyz"

        # Set cookie di client test
        self.client.cookies["_refresh_token"] = bad

        # lakukan request refresh token
        response = self.client.post(reverse("token_refresh"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Token is invalid")

        mock_logger1.warning.assert_called()

        args, kwargs = mock_logger1.warning.call_args

        self.assertEqual(args[0], "Token is invalid")
        self.assertEqual(kwargs["extra"]["event_type"], "token_refresh")
        self.assertEqual(kwargs["extra"]["user_id"], None)
        self.assertEqual(kwargs["extra"]["status"], "failure")
