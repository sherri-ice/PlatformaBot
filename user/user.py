import vk_api


class User:
    def __init__(self):
        self.vk_session = None
        self.tg_id = None

    def init_vk_session(self, token: str):
        self.vk_session = vk_api.VkApi(token)