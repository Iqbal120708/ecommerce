from django.urls import path

from .views import *

urlpatterns = [
    path("province/", ProvinceView.as_view(), name="province"),
    path("province/<int:pk>/", ProvinceView.as_view(), name="province"),
    path("city/", CityView.as_view(), name="city"),
    path("city/<int:pk>/", CityView.as_view(), name="city"),
    path("district/", DistrictView.as_view(), name="district"),
    path("district/<int:pk>/", DistrictView.as_view(), name="district"),
    path("subdistrict/", SubDistrictView.as_view(), name="subdistrict"),
    path("subdistrict/<int:pk>/", SubDistrictView.as_view(), name="subdistrict"),
    path("shipping-address/", ShippingAddressView.as_view(), name="shipping_address"),
    path("shipping-address/<int:pk>/", ShippingAddressView.as_view(), name="shipping_address"),
]
