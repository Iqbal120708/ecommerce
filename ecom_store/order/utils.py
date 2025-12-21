import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from .models import Courier
from shipping_address.utils import format_address
from store.models import Store
from rest_framework import serializers
import logging

logger = logging.getLogger("order")
logger_error = logging.getLogger("order_error")

def fetch_shipping_rates_from_rajaongkir(payload):
    # parameter user for logging error
    
    #couriers = Courier.objects.filter(is_active=True)
    headers = {"key": settings.API_KEY_RAJA_ONGKIR}
    # payload = {
    #     "origin": origin_id,
    #     "destination": destination_id,
    #     "weight": total_weight,
    # }

    results = []
    # for courier in couriers:
    # payload["courier"] = courier.code
    res = requests.post(
        "https://rajaongkir.komerce.id/api/v1/calculate/district/domestic-cost", data=payload, headers=headers
    )

    data = res.json()
    if res.status_code == 200:
        for item in data["data"]:
            results.append(
                {
                    "name": item["name"],
                    "code": item["code"],
                    "service": item["service"],
                    "description": item["description"],
                    "cost": item["cost"],
                    "etd": item["etd"],
                }
            )
    else:
        raise serializers.ValidationError({"error": data["meta"]["message"]})
    return results


def get_origin_and_destination(user, shipping_address_id=None):
    store = Store.objects.filter(is_active=True).first()
    if not store:
        logger_error.error(f"Store aktif tidak ditemukan. User ID: {user.id}")
        raise serializers.ValidationError({"error": "Toko tidak ditemukan."})
        
    origin = store.shipping_address
    
    if shipping_address_id:
        destination = user.shippingaddress_set.filter(id=shipping_address_id).first()
    else:
        destination = user.shippingaddress_set.filter(is_default=True).first()

    if not destination:
        logger.warning(
            f"Destination tidak ditemukan. User ID: {user.id}, Address ID Provided: {shipping_address_id}"
        )
        raise serializers.ValidationError({"error": "Alamat pengiriman belum dipilih. Silakan pilih salah satu alamat Anda atau atur salah satu sebagai 'Alamat Utama' (Default)."
        })
    
    return origin, destination
    
def create_order_details(carts):
    order_details = []

    for cart in carts:
        product = cart.product
    
        order_details.append({
            "product_name": product.name,
            "product_variant_name": product.variant_name,
            "product_price": product.price,
            "product_weight": product.weight,
            "product_width": product.width,
            "product_height": product.height,
            "product_length": product.length,
            "qty": cart.qty,
            "subtotal": product.price * cart.qty,
        })
        
    return order_details
    
    
def calculate_insurance_value(order_details, admin_fee=2000):
    """
    Menghitung premi asuransi pengiriman.
    Default rate: 0.2% (0.002)
    Default admin: Rp 2.000
    """
    total_item_value = sum(item['subtotal'] for item in order_details)
    
    if total_item_value <= 0:
        return 0.0
    
    insurance_rate = 0.002 
    premium = (total_item_value * insurance_rate) + admin_fee
    
    return round(float(premium), 2)

# belum selesai
def create_order_rajaongkir(user, order_details, shipping_context, shipping_option):
    store = Store.objects.filter(is_active=True).first()
    
    headers = {"key": settings.API_KEY_RAJA_ONGKIR}
    
    items_total = sum(item["subtotal"] for item in order_details)
    shipping_cost = shipping_option["cost"]
    insurance_cost = calculate_insurance_value(order_details)
    service_fee = 0
    additional_cost = 0
    shipping_cashback = 0
    
    grand_total = (
        items_total
        + shipping_cost
        - shipping_cashback
        + insurance_cost
    )
    

    order_data = {
        "order_date": str(now().date()),
        "brand_name": store.brand_name,
        "shipper_name": store.name,
        "shipper_phone": store.phone_number,
        "shipper_destination_id": shipping_context["origin_id"],
        "shipper_address": format_address(shipping_context["origin"]),
        #"origin_pin_point": "-7.274631, 109.207174",
        "receiver_name": user.username,
        "receiver_phone": user.phone_number,
        "receiver_destination_id": shipping_context["destination_id"],
        "receiver_address": format_address(shipping_context["destination"]),
        "shipper_email": store.email,
        #"destination_pin_point": "-7.274631, 109.207174",
        "shipping": shipping_option["code"],
        "shipping_type": shipping_option["service"],
        "payment_method": "BANK TRANSFER",
        "shipping_cost": shipping_cost,
        "shipping_cashback": shipping_cashback,
        "service_fee": service_fee,
        "additional_cost": additional_cost,
        "grand_total": int(items_total),
        "cod_value": 0,
        "insurance_value": insurance_cost,
        "order_details": order_details
    }
    
    res = requests.post(
        "https://api-sandbox.collaborator.komerce.id/order/api/v1/orders/store", data=order_data, headers=headers
    )