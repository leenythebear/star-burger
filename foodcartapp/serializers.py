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


