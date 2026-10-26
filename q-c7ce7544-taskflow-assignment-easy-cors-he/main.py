def build_cors_headers(origin, allowed_origins):
    """Return CORS headers for a TaskFlow API response.
    Allowed origin -> echo it with methods + credentials.
    Denied/empty  -> {'Access-Control-Allow-Origin': 'null'}.
    """
    # TODO: implement
    return {}