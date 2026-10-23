def handle_list_tasks(query, tasks):
    result = list(tasks)
    # 1. filter by status if provided
    # 2. validate + apply limit if provided (422 on bad limit)
    # 3. return {'status_code': 200, 'body': result}
    pass