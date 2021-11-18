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
    employee = db.relationship("employee_id", backref = db.backref("employee", uselist = False))
    customer = db.relationship("customer_id", backref = db.backref("customer", uselist = False))

    def add_new_task(self, customer_id, ref, guarantee, platform):
        db.session.add(Task(ref = ref, customer_id = customer_id, guarantee = guarantee, platform = platform))
        apply_db_changes()


task_table = Task()
