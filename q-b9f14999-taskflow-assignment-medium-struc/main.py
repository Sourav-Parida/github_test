def build_log_record(request, seq, allowed_origins):
    """Build one structured log record for a TaskFlow gateway request."""
    method = request.get('method', 'GET').upper()
    path = request.get('path', '/')
    status = request.get('status', 200)
    origin = request.get('origin')

    if status >= 500:
        level = 'error'
    elif status >= 400:
        level = 'warn'
    else:
        level = 'info'

    return {
        'request_id': 'req-%05d' % seq,
        'method': method,
        'path': path,
        'status': status,
        'level': level,
        'cors_allowed': origin in allowed_origins
    }