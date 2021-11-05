import requests
from loader import MAPS_TOKEN


def get_address_from_coordinates(coords: str):
    PARAMS = {
        "apikey": f"{MAPS_TOKEN}",
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": coords
    }
    try:
        r = requests.get(url = "https://geocode-maps.yandex.ru/1.x/", params = PARAMS)
        # получаем данные
        json_data = r.json()
        print(json_data)
        # вытаскиваем из всего пришедшего json именно строку с полным адресом.
        address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["description"]
        # возвращаем полученный адрес
        return address_str
    except Exception as e:
        PARAMS = {
            "apikey": f"{MAPS_TOKEN}",
            "format": "json",
            "lang": "ru_RU",
            "kind": "locality",
            "geocode": coords
        }
        try:
            r = requests.get(url = "https://geocode-maps.yandex.ru/1.x/", params = PARAMS)
            # получаем данные
            json_data = r.json()
            print(json_data)
            # вытаскиваем из всего пришедшего json именно строку с полным адресом.
            address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["description"]
            # возвращаем полученный адрес
            return address_str
        except Exception as e:
            return "error"
