from datetime import datetime

from sql.database import db, apply_db_changes


class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    # check if url is valid
    ref = db.Column(db.String(255))
    completed = db.Column(db.Boolean, default = False)
    guarantee = db.Column(db.Integer)
    creation_date = db.Column(db.Date, default = datetime.now())
    platform = db.Column(db.String(255))


task_table = Task()
