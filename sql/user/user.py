import vk_api
from sql.database import db, apply_db_changes
from vk_auth import authorize_vk_session
from loader import VK_API_APP_ID, VK_CLIENT_SECRET
from enum import Enum


# def get_vk_api(user_id):
#     if get_user_by_tg_id(user_id) is None:
#         return None
#     try:
#         vk_session = vk_api.VkApi(app_id = VK_API_APP_ID, client_secret = VK_CLIENT_SECRET, token = get_user_by_tg_id(
#             user_id).vk_token)
#     except vk_api.exceptions.ApiError as error:
#         return None
#     return vk_session.get_api()


# def ping_vk(user_id):
#     if get_user_by_tg_id(user_id) is None:
#         return UserApiErrors.UNREGISTERED_USER
#     if get_user_by_tg_id(user_id).vk_token is None:
#         return UserApiErrors.VK_NOT_AUTH
#     vk = get_vk_api(user_id)
#     data = vk.users.get()
#     if "deactivated" in data[0]:
#         return UserApiErrors.USER_BANNED
#     return data


# class UserApiErrors(Enum):
#     VK_NOT_AUTH = 1
#     USER_BANNED = 2
#     UNREGISTERED_USER = 3


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
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    employee = db.relationship("Employee", backref = db.backref("employee", uselist = False))
    customer = db.relationship("Customer", backref = db.backref("customer", uselist = False))
    registered_data = db.Column(db.Date)

    def register_vk_token(self, code: str, user_id: int):
        if self.get_user_by_tg_id(user_id) is None:
            return None
        self.get_user_by_tg_id(user_id).vk_token = authorize_vk_session(code, user_id).token['access_token']
        apply_db_changes()

    def get_user_by_tg_id(self, user_id):
        return UserTable.query.filter_by(tg_id = user_id).first()

    def add_new_user(self, tg_id, age = None, salary = None, city = None):
        '''
        Ads new user to database.
        Note: you need to do apply_bd_commit()
        '''
        db.session.add(UserTable(tg_id = tg_id, age = age, salary = salary, city = city))
        return self.get_user_by_tg_id(tg_id)

    def delete_user(user_id):
        UserTable.query.filter_by(id = user_id).delete()
        apply_db_changes()


class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key = True)
    balance = db.Column(db.Integer)
    vk_access_token = db.Column(db.String(255))
    insta_access_token = db.Column(db.String(255))

    def add_employee(self, id):
        '''
        Add new user to employee database.
        '''
        db.session.add(Employee(id = id))
        apply_db_changes()


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key = True)
    balance = db.Column(db.Integer)


user_table = UserTable()
employee_table = Employee()
customer_table = Customer()
