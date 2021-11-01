from sql.database import db, apply_db_changes
from sqlalchemy.dialects.mysql import INTEGER


class Employee(db.Model):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key = True)
    balance = db.Column(INTEGER(usigned = True))
