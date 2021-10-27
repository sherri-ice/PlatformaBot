import json

import vk_api

from loader import VK_API_APP_ID, REDIRECT_FROM_VK, VK_CLIENT_SECRET


# Returns url for vk auth
def request_vk_auth_code(id: int) -> str:
    vk_request_auth_url = "https://oauth.vk.com/authorize?" \
                          f"client_id={VK_API_APP_ID}&" \
                          "scope=friends,status&" \
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


# if __name__ == '__main__':
#     print(request_vk_auth_code(123))
#     vk = vk_api.VkApi(token = "fc33ca223cebea13b5a**26a3813aca733aaeac0b72eb886bcc681c79e4617552d9ce029d60409572aed6")
#     vk.get_api()
#     print(vk.get_api().account.getProfileInfo())
