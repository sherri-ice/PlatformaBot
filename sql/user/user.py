import vk_api
from sql.database import db, apply_db_changes
from vk_auth import authorize_vk_session
from loader import VK_API_APP_ID, VK_CLIENT_SECRET
from enum import Enum


def register_vk_token(code: str, user_id: int):
    if get_user_by_id(user_id) is None:
        return None
    get_user_by_id(user_id).vk_token = authorize_vk_session(code, user_id).token['access_token']
    apply_db_changes()


def get_user_by_id(user_id):
    return UserTable.query.filter_by(id = user_id).first()


def add_new_user(user_id, age = None, salary = None, city = None):
    db.session.add(UserTable(id = user_id, age = age, salary = salary, city = city))
    return get_user_by_id(user_id)


def delete_user(user_id):
    UserTable.query.filter_by(id = user_id).delete()
    apply_db_changes()


def get_vk_api(user_id):
    if get_user_by_id(user_id) is None:
        return None
    try:
        vk_session = vk_api.VkApi(app_id = VK_API_APP_ID, client_secret = VK_CLIENT_SECRET, token = get_user_by_id(
            user_id).vk_token)
    except vk_api.exceptions.ApiError as error:
        return None
    return vk_session.get_api()


def ping_vk(user_id):
    if get_user_by_id(user_id) is None:
        return UserApiErrors.UNREGISTERED_USER
    if get_user_by_id(user_id).vk_token is None:
        return UserApiErrors.VK_NOT_AUTH
    vk = get_vk_api(user_id)
    data = vk.users.get()
    if "deactivated" in data[0]:
        return UserApiErrors.USER_BANNED
    return data


class UserApiErrors(Enum):
    VK_NOT_AUTH = 1
    USER_BANNED = 2
    UNREGISTERED_USER = 3


class UserTable(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True, nullable = False, autoincrement = True)
    tg_id = db.Column(db.Integer)
    # For target
    age = db.Column(db.String(255))
    salary = db.Column(db.String(255))
    city = db.Column(db.String(255))
    #
    appeals = db.Column(db.Integer, default = 0)
    banned = db.Column(db.Boolean, default = False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    employee = db.relationship("Employee", backref = db.backref("employee", uselist = False))


class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key = True)
    balance = db.Column(db.Integer)
