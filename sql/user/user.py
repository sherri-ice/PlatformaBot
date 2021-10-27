import json

from sqlalchemy import TypeDecorator, VARCHAR

from sql.database import db, apply_db_changes
from vk_auth import authorize_vk_session


def register_vk_session(code: str, id: int):
    get_user_by_id(id).vk_session = authorize_vk_session(code, id)
    apply_db_changes()


def get_user_by_id(id):
    return UserTable.query.filter_by(id = id).first()


def add_new_user(id):
    db.session.add(UserTable(id = id))
    apply_db_changes()
    return get_user_by_id(id)


def get_vk_api(id):
    return get_user_by_id(id).vk_session.get_api()


class VkApiType(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class UserTable(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    vk_session = db.Column(VkApiType)
    age = db.Column(db.String, nullable = False)
