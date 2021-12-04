from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from meta.loader import SQL_PASSWORD, SQL_HOST, SQL_USER, SQL_DATABASE

from meta.loader import TELEGRAM_TOKEN
from telebot import TeleBot

bot = TeleBot(token = TELEGRAM_TOKEN)

Base = automap_base()

engine = create_engine(f"mysql+mysqlconnector://{SQL_USER}:{SQL_PASSWORD}@{SQL_HOST}" \
                       f"/{SQL_DATABASE}")

Base.prepare(engine, reflect = True)

Task = Base.classes.task
EmployeesOnTask = Base.classes.employees_on_task
User = Base.classes.user
Employee = Base.classes.employee

session = Session(engine)


def get_tasks_on_guarantee():
    return session.query(Task).filter_by(on_guarantee = True).filter_by(completed =
                                                                        False).all()


def get_tasks_on_guarantee_by_customer_id(customer_id):
    return session.query(Task).filter_by(customer_id = customer_id).filter_by(on_guarantee =
                                                                              True).filter_by(completed =False).all()


def get_task_by_id(task_id):
    return session.query(Task).filter_by(id = task_id).first()


def get_user_by_employee_id(employee_id):
    return session.query(User).filter_by(employee_id = employee_id).first()


def get_employees_by_task_id(task_id):
    return session.query(EmployeesOnTask).filter_by(task_id = task_id).all()


def delete_employee_from_task(employee_id, task_id):
    session.query(EmployeesOnTask).filter_by(task_id = task_id).filter_by(employee_id = employee_id).delete()
    task = get_task_by_id(task_id)
    task.current_count_of_employees -= 1
    session.commit()


def get_pinned_tasks():
    return session.query(Task).filter_by(pinned = True).all()
