from datetime import datetime

import vk_api
from sql.database import db, apply_db_changes
from vk.vk_auth import authorize_vk_session
from meta.loader import VK_API_APP_ID, VK_CLIENT_SECRET


class UserTable(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True, nullable = False, autoincrement = True)
    tg_id = db.Column(db.Integer)
    finished_reg = db.Column(db.Boolean, default = False)
    # For target
    age = db.Column(db.String(255))
    salary = db.Column(db.String(255))
    city_longitude = db.Column(db.Float)
    city_latitude = db.Column(db.Float)
    city_name = db.Column(db.String(255))
    #
    appeals = db.Column(db.Integer, default = 0)
    banned = db.Column(db.Boolean, default = False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    employee = db.relationship("Employee", backref = db.backref("employee", uselist = False))
    customer = db.relationship("Customer", backref = db.backref("customer", uselist = False))
    registered_date = db.Column(db.Date, default = datetime.now())
    vk_access_token = db.Column(db.String(255))

    def register_vk_token(self, tg_id, vk_code):
        if self.get_user_by_tg_id(tg_id) is None:
            return None
        self.get_user_by_tg_id(tg_id).vk_access_token = authorize_vk_session(vk_code, tg_id).token['access_token']
        apply_db_changes()

    def get_user_by_tg_id(self, user_id):
        return self.query.filter_by(tg_id = user_id).first()

    def get_user_by_id(self, id):
        return self.query.filter_by(id = id).first()

    def add_new_user(self, tg_id, age = None, salary = None):
        db.session.add(UserTable(tg_id = tg_id, age = age, salary = salary))
        return self.get_user_by_tg_id(tg_id)

    def delete_user(self, user_id):
        self.query.filter_by(id = user_id).delete()
        if employee_table.get_employee_by_id(user_id) is not None:
            employee_table.query.filter_by(id = user_id).delete()
        if customer_table.get_customer_by_id(user_id) is not None:
            customer_table.query.filter_by(id = user_id).delete()
        apply_db_changes()

    def get_vk_api(self, tg_id):
        if self.get_user_by_tg_id(tg_id) is None:
            return None
        if self.get_user_by_tg_id(tg_id).vk_access_token is None:
            return None
        try:
            vk_session = vk_api.VkApi(app_id = VK_API_APP_ID, client_secret = VK_CLIENT_SECRET,
                                      token = self.get_user_by_tg_id(tg_id).vk_access_token)
            return vk_session.get_api()
        except vk_api.exceptions.ApiError as error:
            return None


class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(db.Integer, primary_key = True)
    balance = db.Column(db.Integer, default = 0)
    appeals = db.Column(db.Integer, default = 0)

    def add_employee(self, user_id):
        '''
        Add new user to employee database.
        '''
        db.session.add(Employee(id = user_id))
        user_table.get_user_by_id(user_id).employee_id = user_id
        apply_db_changes()

    def get_employee_by_id(self, user_id):
        return self.query.filter_by(id = user_id).first()


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key = True)
    balance = db.Column(db.Integer, default = 0)
    appeals = db.Column(db.Integer, default = 0)

    def add_customer(self, user_id):
        db.session.add(Customer(id = user_id))
        user_table.get_user_by_id(user_id).customer_id = user_id
        apply_db_changes()

    def get_customer_by_id(self, user_id):
        return self.query.filter_by(id = user_id).first()


user_table = UserTable()
employee_table = Employee()
customer_table = Customer()
