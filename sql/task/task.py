from sql.database import db, apply_db_changes


class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True, )
