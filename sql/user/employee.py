from sql.database import db, apply_db_changes


class Employee(db.Model):
    balance = db.Column(db.Integer)

    pass
