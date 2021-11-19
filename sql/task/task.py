from datetime import datetime

from sql.database import db, apply_db_changes


class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False, autoincrement = True)
    # check if url is valid
    ref = db.Column(db.String(255))
    completed = db.Column(db.Boolean, default = False)
    guarantee = db.Column(db.Integer)
    on_guarantee = db.Column(db.Boolean, default = False)
    free = db.Column(db.Boolean, default = True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
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
    employee = db.relationship("Employee", backref = db.backref("employee_id", uselist = False))
    customer = db.relationship("Customer", backref = db.backref("customer_id", uselist = False))

    def add_new_task(self, customer_id, ref, guarantee, platform):
        db.session.add(Task(ref = ref, customer_id = customer_id, guarantee = guarantee, platform = platform))
        apply_db_changes()

    def add_new_target_task(self):
        pass

    def get_tasks_by_customer_id(self, customer_id):
        return self.query.filter_by(customer_id = customer_id).all()

    def get_tasks_by_employee_id(self, employee_id):
        return self.query.filter_by(employee_id = employee_id).all()

    # TODO: get targeted task
    def get_new_tasks(self, platform, task_type, filters):
        return self.query.filter(
            self.free == True,
            self.platform == platform,
            self.task_type == task_type
        ).all()

    def set_employee_id_for_task(self, task_id, employee_id):
        task = self.query.filter_by(id = task_id).first()
        if task is None:
            return
        task.employee_id = employee_id
        return


task_table = Task()
