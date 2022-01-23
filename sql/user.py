import math
from datetime import datetime

from sql.exceptions import exceptions

from sql.database import db
from vk.vk_auth import authorize_vk_session, get_vk_api, VkApiError


class UserTable(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    tg_id = db.Column(db.Integer)
    finished_reg = db.Column(db.Boolean, default=False)

    # For target
    age = db.Column(db.String(255))
    sex = db.Column(db.String(1))
    salary = db.Column(db.String(255))
    city_longitude = db.Column(db.Float)
    city_latitude = db.Column(db.Float)
    city_name = db.Column(db.String(255))

    appeals = db.Column(db.Integer, default=0)
    banned = db.Column(db.Boolean, default=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    employee = db.relationship("Employee", backref=db.backref("employee", uselist=False))
    customer = db.relationship("Customer", backref=db.backref("customer", uselist=False))
    registered_date = db.Column(db.Date, default=datetime.now())
    vk_access_token = db.Column(db.String(255))

    def register_vk_token(self, tg_id, vk_code):
        if self.get_user_by_tg_id(tg_id) is None:
            raise exceptions.UserNotFound
        self.get_user_by_tg_id(tg_id).vk_access_token = authorize_vk_session(vk_code, tg_id).token['access_token']

    def get_user_by_tg_id(self, user_id):
        return self.query.filter_by(tg_id=user_id).first()

    def get_user_by_id(self, id):
        return self.query.filter_by(id=id).first()

    def add_new_user(self, tg_id, age=None, salary=None):
        db.session.add(UserTable(tg_id=tg_id, age=age, salary=salary))
        return self.get_user_by_tg_id(tg_id)

    def get_vk_api(self, tg_id):
        if self.get_user_by_tg_id(tg_id) is None:
            raise exceptions.UserNotFound
        if self.get_user_by_tg_id(tg_id).vk_access_token is None:
            raise exceptions.NoVkToken
        try:
            vk_api_session = get_vk_api(vk_token=self.get_user_by_tg_id(tg_id).vk_access_token)
            return vk_api_session
        except VkApiError as error:
            raise error

    def find_employees_for_target_task_by_criteria(self, criteria):
        customers = self.query.filter(UserTable.employee is not None).filter_by(age=criteria['age'])
        if criteria['financial_status'] != 'no_matter':
            customers = self.query.filter(UserTable.employee is not None).filter_by(
                salary=criteria['financial_status'])
        customers = customers.all()
        radius = criteria['radius']
        task_longitude, task_latitude = criteria['longitude'], criteria['latitude']
        result = []
        for customer in customers:
            distance = math.hypot(customer.city_longitude - task_longitude, customer.city_latitude - task_latitude)
        if distance <= radius:
            result.append(customer)
        return result


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    balance = db.Column(db.Integer, default=0)
    appeals = db.Column(db.Integer, default=0)

    def add_customer(self, user_id):
        customer = Customer()
        db.session.add(customer)
        user_table.get_user_by_id(user_id).customer = customer

    def get_customer_by_id(self, user_id):
        return self.query.filter_by(id=user_id).first()


class Employee(db.Model):
    __tablename__ = 'employee'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    balance = db.Column(db.Integer, default=0)
    appeals = db.Column(db.Integer, default=0)

    def add_employee(self, user_id):
        employee = Employee()
        db.session.add(employee)
        user_table.get_user_by_id(user_id).employee = employee

    def get_employee_by_id(self, user_id):
        return self.query.filter_by(id=user_id).first()


user_table = UserTable()
employee_table = Employee()
customer_table = Customer()
