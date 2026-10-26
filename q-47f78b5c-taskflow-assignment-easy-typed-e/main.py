# TaskFlow — Error Signaling (Easy)
# Build a small exception hierarchy and one mapper function.
#
# Requirements:
#   * Base class TaskFlowError(Exception) with class attrs status=500, code='internal_error'.
#   * Subclasses (each sets its own status + code):
#       ValidationError      -> 422, 'validation_error'
#       NotFoundError        -> 404, 'not_found'
#       PermissionDeniedError-> 403, 'permission_denied'
#       ConflictError        -> 409, 'conflict'
#   * error_response(exc) -> {'status': <int>, 'code': <str>, 'message': str(exc)}

class TaskFlowError(Exception):
    status = 500
    code = 'internal_error'

# TODO: define ValidationError, NotFoundError, PermissionDeniedError, ConflictError

def error_response(exc):
    # TODO: return the JSON error body dict
    pass