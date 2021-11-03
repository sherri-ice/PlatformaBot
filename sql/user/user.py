from datetime import datetime

import vk_api
from sql.database import db, apply_db_changes
from vk_auth import authorize_vk_session
from loader import VK_API_APP_ID, VK_CLIENT_SECRET


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
    registered_date = db.Column(db.Date, default = datetime.now())

    def register_vk_token(self, code: str, user_id: int):
        if self.get_user_by_tg_id(user_id) is None:
            return None
        self.get_user_by_tg_id(user_id).vk_token = authorize_vk_session(code, user_id).token['access_token']
        apply_db_changes()

    def get_user_by_tg_id(self, user_id):
        return self.query.filter_by(tg_id = user_id).first()

    def get_user_by_id(self, id):
        return self.query.filter_by(id = id).first()

    def add_new_user(self, tg_id, age = None, salary = None, city = None):
        '''
        Ads new user to database.
        Note: you need to do apply_bd_commit()
        '''
        db.session.add(UserTable(tg_id = tg_id, age = age, salary = salary, city = city))
        return self.get_user_by_tg_id(tg_id)

    def delete_user(self, user_id):
        self.query.filter_by(id = user_id).delete()
        if employee_table.get_employee_by_id(user_id) is not None:
            employee_table.query.filter_by(id = user_id).delete()
        # if customer_table
        apply_db_changes()


class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key = True)
    balance = db.Column(db.Integer, default = 0)
    vk_access_token = db.Column(db.String(255))
    insta_access_token = db.Column(db.String(255))

    def add_employee(self, id):
        '''
        Add new user to employee database.
        '''
        db.session.add(Employee(id = id))
        user_table.get_user_by_id(id).employee_id = id
        apply_db_changes()

    def get_employee_by_id(self, user_id):
        return Employee.query.filter_by(id = user_id).first()


    def get_vk_api(self, user_id):
        if self.get_employee_by_id(user_id) is None:
            return None
        if self.get_employee_by_id(user_id).vk_access_token is None:
            return None
        try:
            vk_session = vk_api.VkApi(app_id = VK_API_APP_ID, client_secret = VK_CLIENT_SECRET,
                                      token = self.get_employee_by_id(
                                          user_id).vk_access_token)
        except vk_api.exceptions.ApiError as error:
            return None
        return vk_session.get_api()

    def register_vk_token(self, tg_id, vk_code):
        user = user_table.get_user_by_tg_id(tg_id)
        self.get_employee_by_id(user.id).vk_access_token = authorize_vk_session(vk_code, tg_id).token['access_token']
        apply_db_changes()


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key = True)
    balance = db.Column(db.Integer)


user_table = UserTable()
employee_table = Employee()
customer_table = Customer()
