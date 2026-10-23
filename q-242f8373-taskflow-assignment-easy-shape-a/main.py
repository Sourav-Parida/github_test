def to_task_response(task):
  title = task.get("title") or ""
  status = task.get("status") or "todo"
  return {
    "task_id": task.get("id"),
    "title": title,
    "status": status,
    "is_completed": status=="done"
  }