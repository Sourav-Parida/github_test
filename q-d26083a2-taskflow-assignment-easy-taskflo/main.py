def create_task(store, task_id, title):
    if task_id in store:
        return ({'error': 'exists'}, 409)
    task = {
        'id': task_id,
        'title': title,
        'status': 'todo'
    }

    store[task_id] = task

    return (task, 201)


def get_task(store, task_id):
    if task_id in store:
        return (store[task_id], 200)

    return (None, 404)