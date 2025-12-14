from django.db import models

from config.models import BaseModel


class Province(BaseModel):
    ro_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)


class City(BaseModel):
    ro_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)


class District(BaseModel):
    ro_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)


class SubDistrict(BaseModel):
    ro_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    zip_code = models.CharField(max_length=10)


class ShippingAddress(BaseModel):
    province = models.ForeignKey(Province, on_delete=models.PROTECT)
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    district = models.ForeignKey(District, on_delete=models.PROTECT)
    subdistrict = models.ForeignKey(SubDistrict, on_delete=models.PROTECT)
    street_address = models.CharField(max_length=255)

    def clean(self):
        if subdistrict.district != district:
            pass

        if district.city != city:
            pass

        if city.province != province:
            pass

    class Meta:
        unique_together = (
            "province",
            "city",
            "district",
            "subdistrict",
            "street_address",
        )


# shi_add = ShippingAddress.objects.filter(
#     province__name__iexact="",
#     city__name__iexact="",
#     district__name__iexact="",
#     subdistrict__name__iexact="",
#     subdistrict__zip_code="",
#     street_address__iexact=""
# ).first()

# if not shi_add:
#     ShippingAddress.objects.create(
#         province__name__iexact="",
#         city__name__iexact="",
#         district__name__iexact="",
#         subdistrict__name__iexact="",
#         subdistrict__zip_code__iexact="",
#         street_address__iexact=""
#     )
