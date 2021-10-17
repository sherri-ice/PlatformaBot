from sql.database import db
from flask import Flask
from views import bot

from loader import SQL_PASSWORD, SQL_HOST, SQL_USER, SQL_DATABASE


def create_app():
    application = Flask(__name__)
    application.config["DEBUG"] = True
    application.config["SQLALCHEMY_DATABASE_URI"] = f"mysql://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}/{SQL_DATABASE}"
    application.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(application)
    application.register_blueprint(bot)
    return application


# if __name__ == "__main__":
#     app = create_app()
#     app.run()
