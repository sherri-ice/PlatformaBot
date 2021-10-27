import requests.utils

from loader import VK_API_APP_ID, REDIRECT_FROM_VK, VK_CLIENT_SECRET


# Returns url for vk auth
def request_vk_auth(id: int) -> str:
    vk_request_auth_url = "https://oauth.vk.com/authorize?" \
                          f"client_id={VK_API_APP_ID}&" \
                          "scope=friends&" \
                          f"redirect_uri={REDIRECT_FROM_VK}?tg_id={id}&" \
                          "response_type=token&" \
                          "v=5.131"
    return vk_request_auth_url


if __name__ == '__main__':
    print(request_vk_auth(832082499))
