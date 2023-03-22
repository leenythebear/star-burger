from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from foodcartapp.serializers import OrderItemsSerializer
from restaurateur.utils.geocoder import (
    get_distance,
    get_coordinates_from_db_or_api,
)


class Login(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=75,
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Укажите имя пользователя",
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        max_length=75,
        required=True,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль"}
        ),
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={"form": form})

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(
            request,
            "login.html",
            context={
                "form": form,
                "ivalid": True,
            },
        )


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("restaurateur:login")


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_products(request):
    restaurants = list(Restaurant.objects.order_by("name"))
    products = list(Product.objects.prefetch_related("menu_items"))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability
            for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False)
            for restaurant in restaurants
        ]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(
        request,
        template_name="products_list.html",
        context={
            "products_with_restaurant_availability": products_with_restaurant_availability,
            "restaurants": restaurants,
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_restaurants(request):
    return render(
        request,
        template_name="restaurants_list.html",
        context={
            "restaurants": Restaurant.objects.all(),
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_orders(request):
    orders = (
        Order.objects.prefetch_related("products")
        .total_price()
        .exclude(status=Order.FINISHED)
        .order_by("status")
    )

    orders_items = []

    for order in orders:
        restaurants_with_coords = []
        if not order.responsible_restaurant:  # Checking if a restaurant is assigned
            customer_coords = get_coordinates_from_db_or_api(order.address)    # Look for available restaurants
            available_restaurants = order.available_restaurants()
            for restaurant in available_restaurants:
                restaurant_coords = get_coordinates_from_db_or_api(
                    restaurant[1]
                )
                distance = get_distance(customer_coords, restaurant_coords)  # Calculate distance
                if isinstance(distance, str):
                    restaurant_with_coords = {
                        "name": restaurant[0],
                        "distance_error": distance,
                    }
                else:
                    restaurant_with_coords = {
                        "name": restaurant[0],
                        "distance": distance,
                    }
                restaurants_with_coords.append(restaurant_with_coords)
        order_items = OrderItemsSerializer(order).data
        order_items['restaurants'] = restaurants_with_coords
        order_items['total_price'] = order.total_price

        orders_items.append(order_items)
    return render(
        request,
        template_name="order_items.html",
        context={"order_items": orders_items},
    )
