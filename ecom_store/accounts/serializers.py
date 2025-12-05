from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    phone_number = PhoneNumberField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user is already registered with this phone number.",
            )
        ],
    )

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["phone_number"] = self.validated_data.get("phone_number")
        return data

    def save(self, request):
        user = super().save(request)
        user.phone_number = self.cleaned_data.get("phone_number")
        user.save()
        return user
