from django.http import JsonResponse
from django.templatetags.static import static

from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Product, Order, OrderProducts
from .serializers import OrderSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def is_correct_field(data, field_name, field_type):
    if field_name not in data:
        return f'`{field_name}` Обязательное поле.'
    elif not data[field_name]:
        return f'`{field_name}` Это поле не может быть пустым'
    elif not isinstance(data[field_name], field_type):
        return f'`{field_name}` Поле должно быть {field_type}'
    return ''


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    saved_order = Order.objects.create(firstname=serializer.validated_data['firstname'],
                                       lastname=serializer.validated_data['lastname'],
                                       phonenumber=serializer.validated_data['phonenumber'],
                                       address=serializer.validated_data['address'])
    for product in serializer.validated_data['products']:
        OrderProducts.objects.create(order=saved_order,
                                     product=product['product'],
                                     quantity=product['quantity'])
    return Response({})
