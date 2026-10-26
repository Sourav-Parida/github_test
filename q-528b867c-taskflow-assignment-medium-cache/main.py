class TaskService:
    def __init__(self, repo, cache, clock):
        self.repo = repo      # callable(task_id) -> dict | None
        self.cache = cache    # dict used as a read cache
        self.clock = clock    # callable() -> iso timestamp

    def get_task(self, task_id):
        # TODO: check cache FIRST; on miss call repo(task_id),
        # store non-None results in cache, return None when not found.
        raise NotImplementedError("Replace this with your solution")

    def status_of(self, task_id):
        # TODO: return the task's status, or 'unknown' when the task is missing.
        raise NotImplementedError("Replace this with your solution")

    def summary(self, ids):
        # TODO: fetch each id (via get_task), skip missing ones, count by status.
        raise NotImplementedError("Replace this with your solution")

    def stamp(self, task_id):
        # TODO: return the task merged with 'checked_at': clock(); None if missing.
        raise NotImplementedError("Replace this with your solution")