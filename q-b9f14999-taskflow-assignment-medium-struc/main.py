def build_log_record(request, seq, allowed_origins):
    """Build one structured log record for a TaskFlow gateway request."""
    method = request.get('method', 'GET').upper()
    path = request.get('path', '/')
    status = request.get('status', 200)
    origin = request.get('origin')
    # TODO: derive level from status and assemble the record
    return {}