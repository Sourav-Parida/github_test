def count_by_status(tasks):
    counts = {}

    for task in tasks:
        status = task['status']
        counts[status] = counts.get(status, 0) + 1

    return counts