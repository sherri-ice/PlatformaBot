import vk_api
from sql.database import db, apply_db_changes
from vk_auth import authorize_vk_session
from loader import VK_API_APP_ID, VK_CLIENT_SECRET


def register_vk_token(code: str, id: int):
    if get_user_by_id(id) is None:
        return None
    get_user_by_id(id).vk_token = authorize_vk_session(code, id).token['access_token']
    apply_db_changes()


def get_user_by_id(id):
    return UserTable.query.filter_by(id = id).first()


def add_new_user(id):
    db.session.add(UserTable(id = id))
    return get_user_by_id(id)


def get_vk_api(id):
    try:
        vk_session = vk_api.VkApi(app_id = VK_API_APP_ID, client_secret = VK_CLIENT_SECRET, token = get_user_by_id(
            id).vk_token)
    except Exception as error:
        return None
    return vk_session.get_api()


class UserTable(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String(255))
    vk_token = db.Column(db.String(255))
    age = db.Column(db.String(255))
    salary = db.Column(db.String(255))
    city = db.Column(db.String(255))
