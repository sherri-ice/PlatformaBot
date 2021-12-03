import datetime

from helpers.helpers_factory import get_pinned_tasks, session


def pinned_task_handler():
    tasks = get_pinned_tasks()
    for task in tasks:
        pinned_date = datetime.datetime.strptime(task.pinned_date, "%m/%d/%y %H:%M")
        if pinned_date + datetime.timedelta(days = 1) < datetime.datetime.utcnow():
            task.pinned = False
            session.commit()
