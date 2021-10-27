import vk_api
from sql.database import db, apply_db_changes
from vk_auth import authorize_vk_session


def register_vk_token(code: str, id: int):
    get_user_by_id(id).vk_token = authorize_vk_session(code, id)
    apply_db_changes()


def get_user_by_id(id):
    return UserTable.query.filter_by(id = id).first()


def add_new_user(id):
    db.session.add(UserTable(id = id))
    apply_db_changes()
    return get_user_by_id(id)


def get_vk_api(id):
    return vk_api.VkApi(token = get_user_by_id(id).vk_token).get_api()


class UserTable(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    vk_token = db.Column(db.String)
    age = db.Column(db.String, nullable = False)
