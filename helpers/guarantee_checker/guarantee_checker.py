import re
from time import sleep
import datetime

from vk.vk_auth import get_vk_api
from helpers.helpers_factory import get_tasks_on_guarantee, get_employees_by_task_id, get_user_by_employee_id, \
    session, delete_employee_from_task, bot, get_tasks_on_guarantee_by_customer_id, get_task_by_id


def guarantee_checker_by_customer_id(customer_id):
    tasks = get_tasks_on_guarantee_by_customer_id(customer_id)
    failed_tasks = []
    for task in tasks:
        employees_id = get_employees_by_task_id(task.id)
        for employee in employees_id:
            result = True
            if task.platform == "vk":
                if task.task_type == "sub":
                    result = check_vk_subscription_task(employee.id, task.ref)
                elif task.task_type == "likes":
                    result = check_vk_like_task(employee.id, task.ref)
                elif task.task_type == "reposts":
                    result = check_vk_repost_task(employee.id, task.ref)
            if not result:
                failed_tasks.append(task.id)
                send_impaired_warranty_message(employee.id, task.id)
    return (True, []) if len(failed_tasks) == 0 else (False, failed_tasks)


def guarantee_checker():
    tasks = get_tasks_on_guarantee()
    for task in tasks:
        employees_id = get_employees_by_task_id(task.id)
        for employee in employees_id:
            result = True
            if task.platform == "vk":
                if task.task_type == "sub":
                    result = check_vk_subscription_task(employee.id, task.ref)
                elif task.task_type == "likes":
                    result = check_vk_like_task(employee.id, task.ref)
                elif task.task_type == "reposts":
                    result = check_vk_repost_task(employee.id, task.ref)
            if not result:
                send_impaired_warranty_message(employee.id, task.id)


def check_vk_like_task(employee_id, post_link):
    vk_api = get_vk_api(get_user_by_employee_id(employee_id).vk_access_token)
    vk_id = vk_api.users.get()[0]['id']
    res = re.search(r"vk\.com\/.+$", post_link)
    post_id = res.string[::-1][:res.string[::-1].find('l')][::-1]
    result = vk_api.wall.get_by_id(posts = [post_id])
    result = vk_api.likes.is_liked(user_id = vk_id, type = 'post', owner_id = result[0]['owner_id'],
                                   item_id = result[0]['id'])
    return result['liked']


def check_vk_repost_task(employee_id, post_link):
    vk_api = get_vk_api(get_user_by_employee_id(employee_id).vk_access_token)
    vk_id = vk_api.users.get()[0]['id']
    res = re.search(r"vk\.com\/.+$", post_link)
    post_id = res.string[::-1][:res.string[::-1].find('l')][::-1]
    result = vk_api.wall.get_by_id(posts = [post_id])
    result = vk_api.likes.is_liked(user_id = vk_id, type = 'post', owner_id = result[0]['owner_id'],
                                   item_id = result[0]['id'])
    return result['copied']


def check_vk_subscription_task(employee_id, page_link):
    vk_api = get_vk_api(get_user_by_employee_id(employee_id).vk_access_token)
    vk_id = vk_api.users.get()[0]['id']
    res = re.search(r"vk\.com\/.+$", page_link)
    page_id = res.string[::-1][:res.string[::-1].find('/')][::-1]
    result = vk_api.utils.resolveScreenName(screen_name = page_id)
    if result['type'] == 'user':
        subs = vk_api.users.get_followers(user_id = result['object_id'])
        return vk_id in subs['items']
    elif result['type'] == 'group':
        return vk_api.groups.is_member(group_id = page_id, user_id = vk_id)


def send_impaired_warranty_message(employee_id, task_id):
    user = get_user_by_employee_id(employee_id)
    user.employee.appeals += 1
    task = get_task_by_id(task_id)
    message_to_user = f"Ты нарушил гарантию!\n\n" \
                      f"Задача №{task_id}\n"
    if task.task_type == "sub":
        message_to_user += f"Подписка: {task.ref}"
    elif task.task_type == "likes":
        message_to_user += f"Лайки: {task.ref}"
    elif task.task_type == "reposts":
        message_to_user += f"Репосты: {task.ref}"
    message_to_user += "\n\nТеперь тебе начислен штраф :с"
    bot.send_message(user.tg_id, message_to_user)
    delete_employee_from_task(employee_id, task_id)
    session.commit()
