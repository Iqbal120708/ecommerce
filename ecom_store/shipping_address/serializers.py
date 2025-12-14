import re

from rest_framework import serializers

from .models import City, District, Province, ShippingAddress, SubDistrict

from .simple_address_serializers import SimpleProvinceSerializer, SimpleCitySerializer, SimpleDistrictSerializer, SimpleSubDistrictSerializer

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ["ro_id", "name"]


class CitySerializer(serializers.ModelSerializer):
    province = ProvinceSerializer(read_only=True)

    class Meta:
        model = City
        fields = ["ro_id", "name", "province"]


class DistrictSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)

    class Meta:
        model = District
        fields = ["ro_id", "name", "city"]


class SubDistrictSerializer(serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)

    class Meta:
        model = SubDistrict
        fields = ["ro_id", "name", "zip_code", "district"]


class ShippingAddressSerializer(serializers.ModelSerializer):
    province = SimpleProvinceSerializer(read_only=True)
    city = SimpleCitySerializer(read_only=True)
    district = SimpleDistrictSerializer(read_only=True)
    subdistrict = SimpleSubDistrictSerializer(read_only=True)
    users = serializers.SerializerMethodField()
    
    province_name = serializers.CharField(max_length=100, write_only=True)
    city_name = serializers.CharField(max_length=100, write_only=True)
    district_name = serializers.CharField(max_length=100, write_only=True)
    subdistrict_name = serializers.CharField(max_length=100, write_only=True)
    zip_code = serializers.CharField(max_length=10, write_only=True)

    class Meta:
        model = ShippingAddress
        fields = [
            "province",
            "city",
            "district",
            "subdistrict",
            "users",
            "street_address",
            "province_name",
            "city_name",
            "district_name",
            "subdistrict_name",
            "zip_code",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        
    def get_users(self, obj):
        users = obj.users.values("id", "username","email")
        return users

    def validate(self, attrs):
        prov_name = attrs.pop("province_name")
        city_name = attrs.pop("city_name")
        dist_name = attrs.pop("district_name")
        subd_name = attrs.pop("subdistrict_name")
        zip_code = attrs.pop("zip_code")

        if not re.fullmatch(r"\d+", zip_code):
            raise serializers.ValidationError("Zip code must be digits.")

        try:
            province = Province.objects.get(name__iexact=prov_name)
        except Province.DoesNotExist:
            raise serializers.ValidationError({"province_name": "Province not found"})

        try:
            city = City.objects.get(name__iexact=city_name, province=province)
        except City.DoesNotExist:
            raise serializers.ValidationError({"city_name": "City not found"})

        try:
            district = District.objects.get(name__iexact=dist_name, city=city)
        except District.DoesNotExist:
            raise serializers.ValidationError({"district_name": "District not found"})

        try:
            subdistrict = SubDistrict.objects.get(
                name__iexact=subd_name, district=district, zip_code=zip_code
            )
        except SubDistrict.DoesNotExist:
            raise serializers.ValidationError(
                {"subdistrict_name": "Subdistrict not found"}
            )

        attrs["province"] = province
        attrs["city"] = city
        attrs["district"] = district
        attrs["subdistrict"] = subdistrict

        return attrs

    def create(self, validated_data):
        province = validated_data.get("province")
        city = validated_data.get("city")
        district = validated_data.get("district")
        subdistrict = validated_data.get("subdistrict")
        street_address = validated_data.get("street_address")
        user = self.context["request"].user

        existing = ShippingAddress.objects.filter(
            province=province,
            city=city,
            district=district,
            subdistrict=subdistrict,
            street_address__iexact=street_address,
        ).first()
        
        if existing:
            existing.users.add(user)
            return existing

        obj = ShippingAddress.objects.create(**validated_data)
        obj.users.add(user)
        return obj


class ShippingAddressListSerializer(serializers.ModelSerializer):
    province = ProvinceSerializer(read_only=True)
    city = CitySerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    subdistrict = SubDistrictSerializer(read_only=True)

    class Meta:
        model = ShippingAddress
        fields = [
            "id",
            "province",
            "city",
            "district",
            "subdistrict",
            "street_address",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
