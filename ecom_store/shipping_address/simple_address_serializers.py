from rest_framework import serializers

from .models import City, District, Province, ShippingAddress, SubDistrict


class SimpleProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ("ro_id", "name")


class SimpleCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("ro_id", "name")


class SimpleDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("ro_id", "name")


class SimpleSubDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubDistrict
        fields = ("ro_id", "name", "zip_code")
