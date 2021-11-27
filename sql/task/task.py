from datetime import datetime

from sql.database import db, apply_db_changes


class EmployeesOnTask(db.Model):
    __tablename__ = "employees_on_task"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    employee_id = db.Column(db.Integer)
    task_id = db.Column(db.Integer)

    def add_employee_to_task(self, employee_id: int, task_id: int):
        db.session.add(EmployeesOnTask(employee_id = employee_id, task_id = task_id))
        apply_db_changes()


class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False, autoincrement = True)
    ref = db.Column(db.String(255))
    needed_count_of_employees = db.Column(db.Integer, default = 0)
    current_count_of_employees = db.Column(db.Integer, default = 0)
    completed = db.Column(db.Boolean, default = False)
    guarantee = db.Column(db.String(255))
    on_guarantee = db.Column(db.Boolean, default = False)
    free = db.Column(db.Boolean, default = True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    creation_date = db.Column(db.Date, default = datetime.now())
    platform = db.Column(db.String(255))
    task_type = db.Column(db.String(255))
    price = db.Column(db.Integer)

    # for target
    age = db.Column(db.Integer)
    city = db.Column(db.String(255))
    salary = db.Column(db.String(255))
    #
    customer = db.relationship("Customer", backref = db.backref("customer_id", uselist = False))

    def add_new_task(self, customer_id, platform, task_type, ref, guarantee, price):
        db.session.add(Task(customer_id = customer_id, platform = platform, task_type = task_type, ref = ref,
                            guarantee = guarantee, price = price))
        apply_db_changes()

    def add_new_target_task(self):
        pass

    def get_tasks_by_customer_id(self, customer_id):
        return self.query.filter_by(customer_id = customer_id).all()

    def get_active_tasks_by_customer_id(self, customer_id):
        return self.query.filter_by(customer_id = customer_id).filter_by(completed = 0).all()

    def get_tasks_by_employee_id(self, employee_id):
        return self.query.filter_by(employee_id = employee_id).all()

    # TODO: get targeted task
    def get_new_tasks(self, platform, task_type, filters):
        return self.query.filter_by(free = 1).filter_by(platform = platform).filter_by(task_type =
                                                                                       task_type).all()


task_table = Task()
