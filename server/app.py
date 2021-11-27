from sql.database import db
from flask import Flask
from routes import bot_handler

from meta.loader import SQL_PASSWORD, SQL_HOST, SQL_USER, SQL_DATABASE


def create_app():
    application = Flask(__name__)
    application.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}" \
                                                    f"/{SQL_DATABASE}"
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(application)
    with application.app_context():
        db.create_all()
    application.register_blueprint(bot_handler)
    return application


if __name__ == '__main__':
    app = create_app()
    app.debug = True
    app.run(port = 4040)
