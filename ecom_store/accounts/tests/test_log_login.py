from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from unittest.mock import patch

User = get_user_model()

class LogLoginTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test",
            email="test@gmail.com",
            password="test2938484jr",
            phone_number="089384442947"
        )
        EmailAddress.objects.create(
            user=cls.user,
            email=cls.user.email,
            verified=True,
            primary=True
        )
        
    @patch("accounts.signals.logger")
    def test_success(self, mock_logger):
        login = self.client.post(
            reverse("rest_login"),
            {
                "email": self.user.email,
                "password": "test2938484jr"
            },
            format="json"
        )
        
        self.assertEqual(login.status_code, 200)
        
        mock_logger.info.assert_called()
        
        args, kwargs = mock_logger.info.call_args
        
        self.assertEqual(args[0], "Login success")
        self.assertEqual(kwargs["extra"]["event_type"], "login")
        self.assertEqual(kwargs["extra"]["user_id"], 1)
        self.assertEqual(kwargs["extra"]["email"], "test@gmail.com")
        