from cart.models import Cart
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Courier


class CheckoutView(APIView):

    def post(self, request):
        if not request.data:
            pass

        ids = request.data.get("cart_ids")
        carts = []
        for pk in ids:
            cart = (
                Cart.objects.filter(user=request.user, pk=pk)
                .select_related("product", "user")
                .first()
            )
            if cart:
                carts.append(cart)

        shipping_address_id = request.data.get("shipping_address_id")
        origin_id, destination_id = get_origin_and_destination(
            request.user, shipping_address_id
        )
        total_weigth = sum([cart.product.weight for cart in carts])

        payload = {
            "origin": origin_id,
            "destination": destination_id,
            "weigth": total_weigth,
        }
        result_res = fetch_shipping_rates_from_rajaongkir(payload)
        return result_res
