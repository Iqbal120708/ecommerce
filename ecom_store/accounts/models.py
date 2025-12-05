import warnings

from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserDeleteWarning(Warning):
    pass


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True)
    pending_delete = models.BooleanField(default=False)
    shipping_address = models.ManyToManyField(
        "shipping_address.ShippingAddress", related_name="users", blank=True
    )

    def delete(self, *args, **kwargs):
        if not self.pending_delete:
            warnings.warn(
                "method delete() di model User dipanggil! Gunakan method soft_delete() untuk delete. Lakukan penghapusan ulang jika tetap ingin menghapus",
                category=UserDeleteWarning,
                stacklevel=2,
            )
            self.pending_delete = True
            super().save(*args, **kwargs)
        else:
            return super().delete(*args, **kwargs)

    def soft_delete(self, *args, **kwargs):
        self.is_active = False
        self.save()
