import requests.utils

from loader import VK_API_APP_ID, REDIRECT_FROM_VK, VK_CLIENT_SECRET


# Returns url for vk auth
def request_vk_auth() -> str:
    vk_request_auth_url = "https://oauth.vk.com/authorize?" \
                          f"client_id={VK_API_APP_ID}&" \
                          "scope=friends&" \
                          f"redirect_uri={REDIRECT_FROM_VK}&" \
                          "response_type=token, id&" \
                          "v=5.131"
    return vk_request_auth_url