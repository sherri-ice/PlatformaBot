from datetime import datetime

from sql.database import db, apply_db_changes
from sqlalchemy import desc, func


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
    # Needed in case of importance overflow
    direct_moving = True
    top_importance = 0
    importance = db.Column(db.Integer, default = 0)
    pinned = db.Column(db.Boolean, default = False)

    # for target
    age = db.Column(db.Integer)
    city = db.Column(db.String(255))
    salary = db.Column(db.String(255))
    #
    customer = db.relationship("Customer", backref = db.backref("customer_id", uselist = False))

    def add_new_task(self, customer_id, platform, task_type, ref, guarantee, price, needed_users):
        db.session.add(Task(customer_id = customer_id, platform = platform, task_type = task_type, ref = ref,
                            guarantee = guarantee, on_guarantee = True if guarantee != "no" else False, price = price, \
                            needed_count_of_employees = needed_users))
        apply_db_changes()

    def add_new_target_task(self):
        pass

    def get_tasks_by_customer_id(self, customer_id):
        return self.query.filter_by(customer_id = customer_id).all()

    def get_task_by_id(self, task_id):
        return self.query.filter_by(id = task_id).first()

    def get_active_tasks_by_customer_id(self, customer_id):
        return self.query.filter_by(customer_id = customer_id).filter_by(completed = 0).all()

    def get_active_tasks_by_employee_id(self, employee_id):
        return EmployeesOnTask.query.filter_by(employee_id = employee_id).count()

    def get_tasks_by_employee_id(self, employee_id):
        return self.query.filter_by(employee_id = employee_id).all()

    def get_tasks_on_guarantee(self):
        return self.query.filter_by(free = False).filter_by(on_guarantee = True).all()

    # TODO: get targeted task
    def get_new_tasks(self, platform, task_type, employee_id):
        tasks = self.query. \
            filter_by(free = 1). \
            filter_by(platform = platform). \
            filter_by(task_type = task_type). \
            order_by(desc(Task.price)). \
            order_by(desc(Task.importance)).all()
        result = []
        for task in tasks:
            if len(EmployeesOnTask.query.filter_by(task_id = task.id).filter_by(employee_id = employee_id).all()) == 0:
                result.append(task)
        return result

    def raise_task_in_top(self, task_id):
        task = self.get_task_by_id(task_id)
        if task is None:
            raise IndexError(f"Invalid task id: {task_id}")
        top_importance = self.query.order_by(desc(Task.importance)).first().importance
        task.importance = top_importance + 1
        apply_db_changes()


task_table = Task()
employees_on_task_table = EmployeesOnTask()
