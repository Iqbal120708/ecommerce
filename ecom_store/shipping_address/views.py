from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import City, District, Province, ShippingAddress, SubDistrict
from .serializers import (CitySerializer, DistrictSerializer,
                          ProvinceSerializer, ShippingAddressSerializer,
                          SubDistrictSerializer)

from django.shortcuts import get_object_or_404

class BaseAddressView(APIView):
    def get(self, request, pk=None):
        model = self.Meta.model
        cls_serializer = self.Meta.serializer

        if pk is not None:
            instance = get_object_or_404(model, pk=pk)
            serializer = cls_serializer(instance)
            return Response(serializer.data)

        name = request.GET.get("name")
        queryset = model.objects.all()

        select_related = getattr(self.Meta, "select_related", [])
        if select_related:
            queryset.select_related(*select_related)

        if name:
            queryset = queryset.filter(name__iexact=name)

        queryset = queryset.order_by("id")
        serializer = cls_serializer(queryset, many=True)
        return Response(serializer.data)


class ProvinceView(BaseAddressView):
    class Meta:
        model = Province
        serializer = ProvinceSerializer


class CityView(BaseAddressView):
    class Meta:
        model = City
        serializer = CitySerializer
        select_related = ["province"]


class DistrictView(BaseAddressView):
    class Meta:
        model = District
        serializer = DistrictSerializer
        select_related = ["city"]


class SubDistrictView(BaseAddressView):
    class Meta:
        model = SubDistrict
        serializer = SubDistrictSerializer

    def get(self, request, pk=None):
        if pk:
            return super().get(request, pk)

        zip_code = request.GET.get("zip_code")
        name = request.GET.get("name")
        model = self.Meta.model

        queryset = model.objects.all().select_related("district")

        if zip_code:
            queryset = queryset.filter(zip_code=zip_code)

        if name:
            queryset = queryset.filter(name__iexact=name)

        queryset = queryset.order_by("id")
        serializer = self.Meta.serializer(queryset, many=True)
        return Response(serializer.data)


class ShippingAddressView(APIView):
    def get(self, request, pk=None):
        if pk:
            instance = (
                ShippingAddress.objects.filter(pk=pk, users=request.user)
                .select_related(
                    "province",
                    "city",
                    "district",
                    "subdistrict",
                )
                .first()
            )
            if not instance: return Response({})
            serializer = ShippingAddressSerializer(instance)
            return Response(serializer.data)

        queryset = ShippingAddress.objects.filter(users=request.user).select_related(
            "province",
            "city",
            "district",
            "subdistrict",
        )
        serializer = ShippingAddressSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ShippingAddressSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
