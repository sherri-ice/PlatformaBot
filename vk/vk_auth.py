import vk_api

from meta.loader import VK_API_APP_ID, REDIRECT_FROM_VK, VK_CLIENT_SECRET

vk_session = vk_api.VkApi(app_id = VK_API_APP_ID, client_secret = VK_CLIENT_SECRET)


# Returns url for vk auth
def request_vk_auth_code(tg_id: int) -> str:
    vk_request_auth_url = "http://oauth.vk.com/authorize?" \
                          f"client_id={VK_API_APP_ID}&" \
                          "scope=friends,status&" \
                          f"redirect_uri={REDIRECT_FROM_VK}?tg_id={tg_id}&" \
                          "response_type=code&" \
                          "v=5.131"
    return vk_request_auth_url


def authorize_vk_session(vk_code: str, tg_id: int):
    try:
        vk_session.code_auth(vk_code, f"{REDIRECT_FROM_VK}?tg_id={tg_id}")
        return vk_session
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return None