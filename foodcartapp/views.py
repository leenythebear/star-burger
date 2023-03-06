from collections import defaultdict

from django.http import JsonResponse
from django.templatetags.static import static

from phonenumber_field.phonenumber import PhoneNumber
from phonenumbers import NumberParseException

from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Product, Order, OrderProducts


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
    order = request.data
    errors = defaultdict(set)
    fields = {
        'firstname': str,
        'lastname': str,
        'phonenumber': str,
        'address': str,
        'products': list
    }
    for field_name, field_type in fields.items():
        error = is_correct_field(order, field_name, field_type)
        if error:
            errors[field_name].add(error)
    if 'phonenumber' in order and isinstance(order['phonenumber'], str):
        try:
            phonenumber = PhoneNumber.from_string(order['phonenumber'], 'RU')
            if not phonenumber.is_valid():
                errors['phonenumber'].add('Введен некорректный номер телефона.')
        except NumberParseException:
            errors['phonenumber'].add('Введен некорректный номер телефона.')

    product_ids = Product.objects.all().values_list('id', flat=True)
    for product in order['products']:
        error = is_correct_field(product, 'product', int)
        if error:
            errors['products'].add(error)
        else:
            if product['product'] not in product_ids:
                errors['products'].add(f"Заказ с несуществующим id продукта."
                                       f"Недопустимый первичный ключ {product['product']}")
        error = is_correct_field(product, 'quantity', int)
        if error:
            errors['products'].add(error)
        else:
            if product['quantity'] < 1:
                errors['products'].add('Количество продуктов должно быть больше 0')

    if errors:
        return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    saved_order = Order.objects.create(firstname=order['firstname'],
                                       lastname=order['lastname'],
                                       phonenumber=order['phonenumber'],
                                       address=order['address'])
    for product in order['products']:
        OrderProducts.objects.create(order=saved_order,
                                     product=Product.objects.get(pk=product['product']),
                                     quantity=product['quantity'])
    return Response({})
