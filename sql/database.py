from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def get_user_by_id(id):
    return User.query.filter_by(id = id).first()


def get_vk_user_by_id(id):
    return VkUser.query.filter_by(id = id).first()


def add_new_user(id):
    db.session.add(User(id = id))
    return get_user_by_id(id)


def register_vk_user(id, access_token, telegram_id):
    db.session.add(VkUser(id = id, vk_access_token = access_token))
    return get_vk_user_by_id(id)


# Ypu should always use this command
def apply_db_changes():
    db.session.commit()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    vk_api = db.relationship('VkUser', backref = 'user', lazy = True)
    age = db.Column(db.String, nullable = False)


class VkUser(db.Model):
    __tablename__ = 'vk_user'
    vk_id = db.Column(db.Integer, primary_key = True)
    vk_access_token = db.Column(db.String, nullable = False)
    telegram_id = db.Column(db.Integer, db.ForeignKey('User.id'))
