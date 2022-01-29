from datetime import datetime

from sql.database import db, apply_db_changes
from sqlalchemy import desc


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
    declined = db.Column(db.Boolean, default = False)
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
    pinned_date = db.Column(db.String(255))

    # for target
    age = db.Column(db.String(255))
    city_longitude = db.Column(db.Float)
    city_latitude = db.Column(db.Float)
    salary = db.Column(db.String(255))
    radius = db.Column(db.Float)

    customer = db.relationship("Customer", backref = db.backref("customer_id", uselist = False))

    def add_new_task(self, customer_id, platform, task_type, ref, guarantee, price, needed_users):
        db.session.add(Task(customer_id = customer_id, platform = platform, task_type = task_type, ref = ref,
                            guarantee = guarantee, on_guarantee = True if guarantee != "no" else False, price = price, \
                            needed_count_of_employees = needed_users))

    def add_new_target_task(self):
        pass

    def get_tasks_by_customer_id(self, customer_id):
        return self.query.filter_by(customer_id = customer_id).all()

    def get_task_by_id(self, task_id):
        return self.query.filter_by(id = task_id).first()

    def get_active_tasks_by_customer_id(self, customer_id, pinned = True):
        result = self.query.filter_by(customer_id = customer_id).filter_by(completed = 0).filter_by(declined = False)
        if not pinned:
            return result.filter_by(pinned = False).all()
        return result.all()

    def get_active_tasks_by_employee_id(self, employee_id):
        return EmployeesOnTask.query.filter_by(employee_id = employee_id).count()

    def get_tasks_by_employee_id(self, employee_id):
        return self.query.filter_by(employee_id = employee_id).all()

    def get_tasks_on_guarantee(self):
        return self.query.filter_by(free = False).filter_by(on_guarantee = True).all()

    # TODO: get targeted task
    def get_new_tasks(self, platform, task_type, employee_id):
        tasks = self.query. \
            filter_by(declined = 0). \
            filter_by(free = 1). \
            filter_by(platform = platform). \
            filter_by(task_type = task_type). \
            order_by(desc(Task.pinned)). \
            order_by(desc(Task.pinned_date)). \
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

    def pin_task(self, task_id):
        task = self.get_task_by_id(task_id)
        if task is None:
            raise IndexError(f"Invalid task id: {task_id}")
        # TODO: write disclaimer
        task.pinned_date = datetime.utcnow().strftime("%m/%d/%y %H:%M")
        task.pinned = True

    def delete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        task.declined = True
        EmployeesOnTask.query.filter_by(task_id = task_id).delete()

    def add_target_task(self, customer_id, platform, task_type, ref, price, age,
                        longitude, latitude, salary, radius):
        db.session.add(Task(customer_id = customer_id, platform = platform, task_type = task_type, ref = ref,
                            price = price, age = age,
                            city_longitude = longitude,
                            city_latitude = latitude, salary = salary, radius = radius))


task_table = Task()
employees_on_task_table = EmployeesOnTask()