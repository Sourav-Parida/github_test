def validate_task_payload(payload):
  errors =[]

  title = payload.get("title")

  if not isinstance(title,str) or title.strip()=="":
    errors.append("title_required")

  if payload.get("status") not in {
    "todo","in_progress","review","done"
  }:
    errors.append("invalid_status")

  if "priority" in payload:
    if payload["priority"] not in {"low","medium","high"}:
      errors.append("invalid_priority")

  if "estimate_hours" in payload:
    value = payload["estimate_hours"]

    if(
      isinstance(value,bool)
      or not isinstance(value,(int,float))
      or value <0
    ):
      errors.append("invalid_estimate")
  errors.sort()

  return{
    "valid":len(errors) ==0,
    "errors":errors
  }
