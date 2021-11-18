# from instagram import InstagramAPI
#
# from loader import INSTA_API_APP_ID, INSTA_CLIENT_SECRET, REDIRECT_FROM_INSTA
# import requests
#
#
# # Returns url for vk auth
# def request_insta_auth_code() -> str:
#     insta_request_auth_url = f"https://www.instagram.com/oauth/authorize?client_id=" \
#                              f"{INSTA_API_APP_ID}&redirect_uri={REDIRECT_FROM_INSTA}&scope=user_profile," \
#                              f"user_media&response_type=code"
#     return insta_request_auth_url
#
#
# api = InstagramAPI(client_id = INSTA_API_APP_ID, client_secret = INSTA_CLIENT_SECRET,
#                    redirect_uri = REDIRECT_FROM_INSTA)
#
# if __name__ == '__main__':
#     print(request_insta_auth_code())
#     code = (str(input("Paste in code in query string after redirect: ").strip()))
#     url = "https://api.instagram.com/oauth/access_token"
#     data = {"client_id": INSTA_API_APP_ID, "client_secret": INSTA_CLIENT_SECRET, "grant_type": "authorization_code",
#             "redirect_uri": REDIRECT_FROM_INSTA, "code": code}
#
#     print(requests.post(url = url, data = data).)
#
