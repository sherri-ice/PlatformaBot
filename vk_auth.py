from loader import VK_API_APP_ID, REDIRECT_FROM_VK


# Returns url for vk auth
def request_vk_auth() -> str:
    vk_auth_url = "https://oauth.vk.com/authorize?" \
                  f"client_id={VK_API_APP_ID}&" \
                  "scope=friends&" \
                  f"redirect_uri={REDIRECT_FROM_VK}&" \
                  "response_type=code&" \
                  "v=5.131"
    return vk_auth_url