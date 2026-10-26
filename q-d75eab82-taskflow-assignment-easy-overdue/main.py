class TaskService:
    def __init__(self, repo, clock):
        # store the injected dependencies (do NOT create them here)
        self.repo = repo      # callable() -> list[dict]
        self.clock = clock    # callable() -> 'YYYY-MM-DD'

    def overdue_count(self):
        # TODO: a task is overdue when it HAS a due date, is NOT 'done',
        # and its due date is STRICTLY before clock(). Return the count.
        pass