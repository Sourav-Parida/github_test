def create_task(store, task_id, title, status='todo'):
    if task_id in store:
        return ({'error': 'exists'}, 409)
    task = {
        'id': task_id,
        'title': title,
        'status': status
    }
    store[task_id] = task
    return (task, 201)


def get_task(store, task_id):
    if task_id in store:
        return (store[task_id], 200)
    return (None, 404)


def update_task(store, task_id, fields):
    if task_id not in store:
        return (None, 404)
    task = store[task_id]
    for key, value in fields.items():
        if key != 'id':
            task[key] = value
    return (task, 200)


def delete_task(store, task_id):
    if task_id not in store:
        return (None, 404)
    del store[task_id]
    return (True, 200)


def list_tasks(store, status=None):
    tasks = list(store.values())
    if status is not None:
        tasks = [
            task for task in tasks
            if task.get('status') == status
        ]
    return (tasks, 200)