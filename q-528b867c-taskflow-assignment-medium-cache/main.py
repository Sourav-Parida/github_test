class TaskService:
    def __init__(self, repo, cache, clock):
        self.repo = repo
        self.cache = cache
        self.clock = clock

    def get_task(self, task_id):
        # Check cache first
        if task_id in self.cache:
            return self.cache[task_id]

        # Fetch from repository on cache miss
        task = self.repo(task_id)

        # Cache only non-None results
        if task is not None:
            self.cache[task_id] = task

        return task

    def status_of(self, task_id):
        task = self.get_task(task_id)

        if task is None:
            return 'unknown'

        return task.get('status', 'unknown')

    def summary(self, ids):
        counts = {}

        for task_id in ids:
            task = self.get_task(task_id)

            if task is None:
                continue

            status = task.get('status', 'unknown')
            counts[status] = counts.get(status, 0) + 1

        return counts

    def stamp(self, task_id):
        task = self.get_task(task_id)

        if task is None:
            return None

        return {
            **task,
            'checked_at': self.clock()
        }