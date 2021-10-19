from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_user_by_id(id):
    return User.query.filter_by(id = id).first()


def add_new_user(id):
    db.session.add(User(id = id))
    return get_user_by_id(id)


# Ypu should always use this command
def apply_db_changes():
    db.session.commit()


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    vk_api = db.Column(db.String)
    age = db.Column(db.String, nullable = False)
