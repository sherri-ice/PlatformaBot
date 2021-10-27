import vk_api
from vk_api import VkApi

from sql.database import db


def register_vk_session(id, token):
    get_user_by_id(id).vk_session = VkApi(token)


def get_user_by_id(id):
    return UserTable.query.filter_by(id = id).first()


def add_new_user(id):
    db.session.add(UserTable(id = id))
    return get_user_by_id(id)


class UserTable(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    vk_session = db.Column(db.String)
    age = db.Column(db.String, nullable = False)
