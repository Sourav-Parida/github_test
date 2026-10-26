import jwt

# TaskFlow now issues tokens that may carry an expiry ("exp") and must be
# verified with clear, distinct outcomes for the caller.

def issue_token(user_id, role, secret, exp_ts=None):
    """Sign {"sub": user_id, "role": role} (add "exp": exp_ts when given)."""
    payload = {"sub": user_id, "role": role}
    # TODO: add exp when exp_ts is not None, then jwt.encode(...)
    pass

def verify_token(token, secret):
    """Return the claims dict when valid; otherwise return one of the strings
    "expired", "invalid_signature", or "invalid_token"."""
    # TODO: decode inside try/except; order the pyjwt exceptions correctly
    pass

def extract_role(token, secret):
    """Return the role string, or "invalid" if the token cannot be trusted."""
    pass