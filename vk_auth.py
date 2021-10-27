import json

import vk_api

from loader import VK_API_APP_ID, REDIRECT_FROM_VK, VK_CLIENT_SECRET


# Returns url for vk auth
def request_vk_auth_code(id: int) -> str:
    vk_request_auth_url = "https://oauth.vk.com/authorize?" \
                          f"client_id={VK_API_APP_ID}&" \
                          "scope=friends,status,nohttps&" \
                          f"redirect_uri={REDIRECT_FROM_VK}?tg_id={id}&" \
                          "response_type=code&" \
                          "v=5.131"
    return vk_request_auth_url


def authorize_vk_session(code: str, id: int):
    vk_session = vk_api.VkApi(app_id = VK_API_APP_ID, client_secret = VK_CLIENT_SECRET)
    try:
        vk_session.code_auth(code, f"{REDIRECT_FROM_VK}?tg_id={id}")
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return None
    return vk_session.token


if __name__ == '__main__':
    print(request_vk_auth_code(123))
    vk = vk_api.VkApi(token = "a003e0714b73a86aa7cb55609a076769131bccc1b6cf94cc7ac98e5ffd3e0d7d3050821ebe7e5c5f4aa53")
    print(vk.get_api().account.getInfo())
