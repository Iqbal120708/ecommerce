import requests
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Courier


def fetch_shipping_rates_from_rajaongkir(payload):
    couriers = Courier.objects.filter(is_active=True)

    headers = {"key": settings.API_KEY_RAJA_ONGKIR}
    payload = {
        "origin": origin_id,
        "destination": destination_id,
        "weigth": total_weigth,
    }

    results = []
    for courier in couriers:
        payload["courier"] = courier.code
        res = requests.post(
            "https://api.rajaongkir.com/starter/cost", data=payload, headers=headers
        )

        if res.status_code == 200:
            data = res.json()["results"]
            if data["costs"]:
                results.append(
                    {
                        "code": data["code"],
                        "name": courier.name,
                        "service": data["costs"]["service"],
                        "description": data["costs"]["description"],
                        "price": data["costs"]["cost"]["value"],
                        "etd": data["costs"]["cost"]["etd"],
                    }
                )
    return results


def get_origin_and_destination(user, shipping_address_id=None):
    User = get_user_model()
    superadmins = User.objects.filter(is_superuser=True).first()
    if not superadmins or superadmins == user:
        pass
    origin = superadmins.shipping_address.filter(is_default=True).first()
    if not origin:
        pass
    destination = user.shipping_address.filter(is_default=True).first()
    if not destination:
        destination = user.shipping_address.filter(id=shipping_address_id).first()
        if not destination:
            pass

    return origin.city.ro_id, destination.city.ro_id
