import os

import requests
from dotenv import load_dotenv
from geopy import distance

from star_burger import settings


def fetch_coordinates(address):
    apikey = settings.YANDEX_API_KEY
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_distance(customer_coordinates, restaurant_coordinates):
    return distance.distance(customer_coordinates, restaurant_coordinates)


if __name__ == '__main__':
    load_dotenv()
    api_key = os.getenv('YANDEX_KEY')
    coords1 = fetch_coordinates(api_key, 'Электросила')
    coords2 = fetch_coordinates(api_key, 'Ключевская сопка')
    print(get_distance(coords1, coords2))
