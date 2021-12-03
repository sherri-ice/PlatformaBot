from datetime import datetime
from time import sleep

from guarantee_checker.guarantee_checker import guarantee_checker
from pinned_tasks_handler.pinned_tasks_handler import pinned_task_handler


def helpers_loop():
    # Waits time to be "rounded", e.g. "12:00"
    sleep(60 * (60 - datetime.now().minute))
    while True:
        # Sleep for one hour
        guarantee_checker()
        pinned_task_handler()
        sleep(60 * 60)


if __name__ == '__main__':
    helpers_loop()
