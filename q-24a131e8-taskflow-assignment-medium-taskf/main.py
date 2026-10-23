def create_task(store, task_id, title, status='todo'):
    raise NotImplementedError("Write your solution here")
def get_task(store, task_id):
    # TODO: (task, 200) if present else (None, 404)
    raise NotImplementedError("Write your solution here")
def update_task(store, task_id, fields):
    # TODO: (None, 404) if missing
    # TODO: apply fields but NEVER allow 'id' to change; return (task, 200)
    raise NotImplementedError("Write your solution here")
def delete_task(store, task_id):
    # TODO: (True, 200) on success else (None, 404)
    raise NotImplementedError("Write your solution here")
def list_tasks(store, status=None):
    # TODO: return (list_of_tasks, 200); when status is given, filter by it
    raise NotImplementedError("Write your solution here")