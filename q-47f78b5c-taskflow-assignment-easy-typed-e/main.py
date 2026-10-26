class TaskFlowError(Exception):
    status = 500
    code = 'internal_error'


class ValidationError(TaskFlowError):
    status = 422
    code = 'validation_error'


class NotFoundError(TaskFlowError):
    status = 404
    code = 'not_found'


class PermissionDeniedError(TaskFlowError):
    status = 403
    code = 'permission_denied'


class ConflictError(TaskFlowError):
    status = 409
    code = 'conflict'


def error_response(exc):
    return {
        'status': exc.status,
        'code': exc.code,
        'message': str(exc)
    }