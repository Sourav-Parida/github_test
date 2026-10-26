# TaskFlow — Error Signaling (Medium)
# A validation layer that RAISES, wrapped by a caller that CATCHES into an error dict.
#
# validate_task(payload) raises ValidationError(message, field=...) on the FIRST bad field:
#   * title: required, non-empty string (after strip)      -> field 'title'
#   * status: optional, default 'todo', in {todo,in_progress,done} -> field 'status'
#   * priority: optional, default 'medium', in {low,medium,high}   -> field 'priority'
#   * estimate_hours: optional; if present must be a real number >= 0 (bool is NOT a number)
#                                                          -> field 'estimate_hours'
#   * non-dict payload -> ValidationError('payload must be an object', field=None)
#   On success returns {'title': <stripped>, 'status': ..., 'priority': ...}
#
# submit_task(payload) calls validate_task and returns:
#   success -> {'ok': True, 'task': <validated dict>}
#   failure -> {'ok': False, 'error': {'status':422,'code':'validation_error','message':...,'field':...}}

class TaskFlowError(Exception):
    status = 500
    code = 'internal_error'

class ValidationError(TaskFlowError):
    status = 422
    code = 'validation_error'
    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field

def validate_task(payload):
    # TODO: raise ValidationError on the first invalid field; return normalized dict on success
    pass

def submit_task(payload):
    # TODO: call validate_task inside try/except and shape the response
    pass