from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from foodcartapp.models import OrderProducts, Order


class OrderProductsSerializer(ModelSerializer):
    class Meta:
        model = OrderProducts
        fields = ["order", "product", "quantity"]

    def create(self, validated_data):
        price = validated_data['product'].price
        return OrderProducts.objects.create(price=price, **validated_data)


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "firstname",
            "lastname",
            "phonenumber",
            "address",
        ]

    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
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

