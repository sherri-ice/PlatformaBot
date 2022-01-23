import requests
from resourses.loader import MAPS_TOKEN

yandex_maps_url = "https://geocode-maps.yandex.ru/1.x/"


def get_address_from_coordinates(coords: str):
    """
    :param coords:
    :return: address str
    """

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
            return f"Geo patcher error: {coords} can't be recognized."


if __name__ == '__main__':
    print(get_address_from_coordinates("33.44444, 52.4"))
