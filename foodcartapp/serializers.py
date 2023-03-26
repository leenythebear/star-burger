from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from foodcartapp.models import OrderProducts, Order


class OrderProductsSerializer(ModelSerializer):
    class Meta:
        model = OrderProducts
        fields = ["product", "quantity"]


class OrderSerializer(ModelSerializer):
    products = OrderProductsSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = [
            "firstname",
            "lastname",
            "phonenumber",
            "address",
            "products",
        ]

    def create(self, validated_data):
        products = validated_data.pop('products')

        order = Order.objects.create(**validated_data)
        for product in products:
            price = product['product'].price
            OrderProducts.objects.create(order=order, price=price, **product)
        return order


class OrderItemsSerializer(ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    payment_type = serializers.CharField(source='get_payment_type_display')
    responsible_restaurant = serializers.CharField(source='responsible_restaurant.name', default='')

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "payment_type",
            "responsible_restaurant",
            "firstname",
            "lastname",
            "phonenumber",
            "address",
            "comment",
        ]

