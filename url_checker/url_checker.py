import requests
import validators
import re
from meta.loader import TELEGRAM_TOKEN
from vk.vk_auth import get_service_token_session


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


def vk_page_check(url: str):
    if not base_url_check(url):
        return False, "wrong url"
    vk_api = get_service_token_session()
    res = re.search(r"vk\.com\/.+$", url)
    if res is None:
        return False, "wrong url"
    vk_screen_name = res.string[::-1][:res.string[::-1].find('/')][::-1]
    result = vk_api.utils.resolveScreenName(screen_name = vk_screen_name)
    if len(result) == 0:
        return False, "wrong url"
    if result['type'] == 'user':
        vk_user_info = vk_api.users.get(user_ids = vk_screen_name)
        if 'deactivated' in vk_user_info[0]:
            return False, "banned user"
        return True, "{} {}".format(vk_user_info[0]["first_name"], vk_user_info[0]["last_name"])
    elif result['type'] == 'group':
        vk_group_info = vk_api.groups.getById(group_id = vk_screen_name)
        if vk_group_info[0]['is_closed']:
            return False, "closed group"
        else:
            return True, vk_group_info[0]['name']
    return False, ""