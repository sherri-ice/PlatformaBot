from flask_testing import TestCase
from flask import Flask

from sql.database import db
from sql.user import UserTable


class Test(TestCase):
    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        db.init_app(app)
        return app

    def setUp(self) -> None:
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

    def test_simple(self):
        user = UserTable()
        db.session.add(user)
        db.session.commit()
        assert user in db.session
