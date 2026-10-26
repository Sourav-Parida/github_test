def build_cors_headers(origin, allowed_origins):
    """Return CORS headers for a TaskFlow API response."""
    if not origin or origin not in allowed_origins:
        return {
            'Access-Control-Allow-Origin': 'null'
        }

    return {
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE',
        'Access-Control-Allow-Credentials': 'true'
    }