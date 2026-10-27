class TaskService:
    def __init__(self, repo, clock):
        self.repo = repo
        self.clock = clock

    def overdue_count(self):
        today = self.clock()
        tasks = self.repo()
        count = 0

        for task in tasks:
            due_date = task.get('due')
            status = task.get('status')

            if due_date is not None and status != 'done' and due_date < today:
                count += 1

        return count