import requests
from django.utils import timezone
from geopy import distance

from addresses.models import Address
from star_burger import settings


def fetch_coordinates(api_key, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": api_key,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"][
        "featureMember"
    ]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return lon, lat


def get_coordinates_from_db_or_api(address):
    api_key = settings.YANDEX_API_KEY
    try:
        address_obj = Address.objects.get(address=address)
        lat = address_obj.lat
        lon = address_obj.lon
        return lat, lon
    except Address.DoesNotExist:
        pass
    try:
        coords = fetch_coordinates(api_key, address)
    except (requests.exceptions.HTTPError, KeyError):
        coords = None

    address_obj = Address(address=address, updated_at=timezone.now())
    if coords is None:
        lon, lat = None, None
    else:
        lon, lat = coords
        address_obj.lon = lon
        address_obj.lat = lat
    address_obj.save()
    return lat, lon


def get_distance(customer_coordinates, restaurant_coordinates):
    if all([*customer_coordinates, *restaurant_coordinates]):
        distance_between = (round(distance.distance(customer_coordinates, restaurant_coordinates).km, 1))
        return distance_between
