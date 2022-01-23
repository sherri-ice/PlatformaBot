import requests
from setup import MAPS_TOKEN


def get_address_from_coordinates(coords: str):
    """
    Warning! This function requires coordinates to be in this order: longitude, latitude.
    Otherwise, Yandex Map API won't work correctly!
    :param coords:
    :return: address str
    """
    yandex_maps_url = "https://geocode-maps.yandex.ru/1.x/"

    def make_response_and_parse(params):
        r = requests.get(url = yandex_maps_url, params = PARAMS)
        json_data = r.json()
        address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["description"]
        return address_str

    PARAMS = {
        "apikey": f"{MAPS_TOKEN}",
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": coords
    }
    try:
        # Gets address from maps.yandex.ru api, house
        address = make_response_and_parse(PARAMS)
        return address
    except IndexError as e:
        # If house didn't work, gets locality
        PARAMS["kind"] = "locality"
        try:
            address = make_response_and_parse(PARAMS)
            return address
        except IndexError as e:
            raise IndexError(f"Geo patcher error: {coords} can't be recognized.")
