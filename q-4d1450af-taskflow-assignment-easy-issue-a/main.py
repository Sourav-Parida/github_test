import jwt

# TaskFlow issues HS256 access tokens carrying who the user is ("sub")
# and what they can do ("role"). Implement the three helpers below.

def issue_token(user_id, role, secret):
    """Return an HS256 JWT whose payload is {"sub": user_id, "role": role}."""
    # TODO: use jwt.encode(...) with algorithm="HS256"
    pass

def read_claims(token, secret):
    """Decode the token and return its claims dict."""
    # TODO: use jwt.decode(...) with algorithms=["HS256"]
    pass

def token_is_valid(token, secret):
    """Return True if the token decodes under `secret`, else False."""
    # TODO: try to decode; catch jwt.InvalidTokenError
    pass