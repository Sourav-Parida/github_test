import jwt

def issue_token(user_id, role, secret, exp_ts=None):
    """Sign {"sub": user_id, "role": role} (add "exp": exp_ts when given)."""
    payload = {"sub": user_id, "role": role}

    if exp_ts is not None:
        payload["exp"] = exp_ts

    return jwt.encode(payload, secret, algorithm="HS256")


def verify_token(token, secret):
    """Return claims when valid; otherwise return an error string."""
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])

    except jwt.ExpiredSignatureError:
        return "expired"

    except jwt.InvalidSignatureError:
        return "invalid_signature"

    except jwt.InvalidTokenError:
        return "invalid_token"


def extract_role(token, secret):
    """Return the role string, or 'invalid' if the token cannot be trusted."""
    result = verify_token(token, secret)

    if isinstance(result, dict):
        role = result.get("role")
        if isinstance(role, str):
            return role

    return "invalid"