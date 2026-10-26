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
    if not isinstance(payload, dict):
        raise ValidationError('payload must be an object', field=None)

    # Validate title
    title = payload.get('title')
    if not isinstance(title, str) or not title.strip():
        raise ValidationError(
            'title must be a non-empty string',
            field='title'
        )

    # Validate status
    status = payload.get('status', 'todo')
    if status not in {'todo', 'in_progress', 'done'}:
        raise ValidationError(
            'status must be todo, in_progress, or done',
            field='status'
        )

    # Validate priority
    priority = payload.get('priority', 'medium')
    if priority not in {'low', 'medium', 'high'}:
        raise ValidationError(
            'priority must be low, medium, or high',
            field='priority'
        )

    # Validate estimate_hours
    if 'estimate_hours' in payload:
        estimate = payload['estimate_hours']

        if isinstance(estimate, bool) or not isinstance(estimate, (int, float)) or estimate < 0:
            raise ValidationError(
                'estimate_hours must be a number >= 0',
                field='estimate_hours'
            )

    return {
        'title': title.strip(),
        'status': status,
        'priority': priority
    }


def submit_task(payload):
    try:
        task = validate_task(payload)
        return {
            'ok': True,
            'task': task
        }
    except ValidationError as exc:
        return {
            'ok': False,
            'error': {
                'status': exc.status,
                'code': exc.code,
                'message': str(exc),
                'field': exc.field
            }
        }