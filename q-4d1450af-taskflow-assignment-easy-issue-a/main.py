import jwt

def issue_token(user_id, role, secret):
    """Return an HS256 JWT whose payload is {"sub": user_id, "role": role}."""
    payload = {
        "sub": user_id,
        "role": role
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def read_claims(token, secret):
    """Decode the token and return its claims dict."""
    return jwt.decode(token, secret, algorithms=["HS256"])


def token_is_valid(token, secret):
    """Return True if the token decodes under `secret`, else False."""
    try:
        jwt.decode(token, secret, algorithms=["HS256"])
        return True
    except jwt.InvalidTokenError:
        return False