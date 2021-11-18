from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Ypu should always use this command
def apply_db_changes():
    db.session.commit()
