import requests
import validators
import re
from meta.loader import TELEGRAM_TOKEN


def base_url_check(url: str):
    if not validators.url(url):
        return False
    else:
        return True


def telegram_channel_check(url: str):
    if not base_url_check(url):
        return False, ""
    res = re.search(r"t\.me\/.+$", url)
    if res is None:
        return False, ""
    # Cut the channel name
    channel_name = res.string[::-1][:res.string[::-1].find('/')][::-1]
    request_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id" \
                  f"=@{channel_name}&text=123"
    response = requests.get(request_url)
    if response.json()["ok"]:
        return False, ""
    response = response.json()
    if response["description"] == "Bad Request: chat not found":
        return False
    return True, channel_name
