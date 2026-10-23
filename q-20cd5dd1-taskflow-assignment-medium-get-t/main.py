def handle_list_tasks(query, tasks):
    result = list(tasks)

    if 'status' in query:
        result = [
            task for task in result
            if task.get('status') == query['status']
        ]

    if 'limit' in query:
        try:
            limit = int(query['limit'])
            if limit <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return {
                'status_code': 422,
                'body': {'error': 'invalid limit'}
            }
        result = result[:limit]

    return {
        'status_code': 200,
        'body': result
    }