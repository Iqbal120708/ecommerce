import random
import re
import time
from unittest.mock import patch

from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse
from freezegun import freeze_time
from rest_framework.test import APITestCase

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ACCOUNT_EMAIL_VERIFICATION="mandatory",
)
class VerificationTest(APITestCase):
    def register_user(self):
        url = reverse("rest_register")
        data = {
            "username": f"user{time.time()}",
            "email": f"user{time.time()}@mail.com",
            "password1": "Tes12345!",
            "password2": "Tes12345!",
            "phone_number": f"+6281234567{random.randint(10,99)}",
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, 201)

        return data

    def test_success(self):
        """
        Test verifikasi email sukses:
        - register user
        - ambil email verifikasi
        - ambil link & key
        - POST ke custom verify
        - assert response
        """

        # Register
        reg = self.register_user()

        # Pastikan email terkirim
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body

        # Ambil key verifikasi dari email
        match = re.search(r"http[s]?://\S+", email_body)
        assert match is not None
        link = match.group()

        response = self.client.post(link)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Email successfully confirmed.")

    @freeze_time("2025-12-05")
    def test_link_invalid(self):
        """
        Test verifikasi email sukses:
        - register user
        - ambil email verifikasi
        - ambil link & key
        - ubah link agar invalid
        - POST ke custom verify
        - assert response
        """

        # Register
        reg = self.register_user()

        # Pastikan email terkirim
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body

        # Ambil key verifikasi dari email
        match = re.search(r"http[s]?://\S+", email_body)
        assert match is not None
        link = match.group()

        with freeze_time("2025-12-09"):  # loncat 4 hari
            response = self.client.post(link)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"], "Invalid or expired verification key."
        )

    def test_email_address_verified(self):
        """
        Test verifikasi email sukses:
        - register user
        - ambil data EmailAddress ubah verified = True
        - ambil email verifikasi
        - ambil link & key
        - POST ke custom verify
        - assert response
        """

        # Register
        reg = self.register_user()

        # Ubah status verified
        email_address = EmailAddress.objects.get(email=reg["email"])
        email_address.verified = True
        email_address.save()

        # Pastikan email terkirim
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body

        # Ambil key verifikasi dari email
        match = re.search(r"http[s]?://\S+", email_body)
        assert match is not None
        link = match.group()

        response = self.client.post(link)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"], "Invalid or expired verification key."
        )

    def test_exception(self):
        """
        Test verifikasi email error:
        - register user
        - ambil email verifikasi
        - ambil link & key
        - buat confirm() melempar exception
        - POST ke custom verify
        - assert response
        """

        # Register
        reg = self.register_user()

        # Pastikan email terkirim
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body

        # Ambil link dari email
        match = re.search(r"http[s]?://\S+", email_body)
        assert match is not None
        link = match.group()

        # Patch confirm() supaya memicu exception
        with patch.object(
            EmailConfirmationHMAC, "confirm", side_effect=Exception("error test")
        ):
            response = self.client.post(link)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Verification failed: error test")
