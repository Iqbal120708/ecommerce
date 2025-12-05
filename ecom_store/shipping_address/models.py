from django.db import models

from config.models import BaseModel


# Create your models here.
class ShippingAddress(BaseModel):
    province_id_ro = models.IntegerField()
    city_id_ro = models.IntegerField()
    district_id_ro = models.IntegerField()
    street_address = models.CharField(max_length=255)
    postal_code = models.IntegerField()

    class Meta:
        unique_together = (
            "province_id_ro",
            "city_id_ro",
            "district_id_ro",
            "street_address",
            "postal_code",
        )
