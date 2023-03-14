from rest_framework.serializers import ModelSerializer

from foodcartapp.models import OrderProducts, Order


class OrderProductsSerializer(ModelSerializer):
    class Meta:
        model = OrderProducts
        fields = ["id", "product", "quantity"]


class OrderSerializer(ModelSerializer):
    products = OrderProductsSerializer(
        many=True, allow_empty=False, write_only=True
    )

    class Meta:
        model = Order
        fields = [
            "firstname",
            "lastname",
            "phonenumber",
            "address",
            "products",
        ]
