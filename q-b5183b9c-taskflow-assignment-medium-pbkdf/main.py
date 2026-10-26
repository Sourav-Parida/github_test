import hashlib

ITERATIONS = 100000

def hash_password(password, salt, iterations=ITERATIONS):
    """Return hashlib.pbkdf2_hmac('sha256', ...) as a hex string.
    salt is bytes; encode the password as utf-8."""
    # TODO
    raise NotImplementedError("Replace this with your solution")

def make_record(password, salt, iterations=ITERATIONS):
    """Return a record string 'iterations$salt_hex$hash_hex'
    (use salt.hex() for the salt portion)."""
    # TODO
    raise NotImplementedError("Replace this with your solution")

def verify_password(password, record):
    """Parse record back into iterations/salt/hash, recompute the hash for
    `password`, and return True only if it matches. Return False for any
    malformed record instead of raising."""
    # TODO
    raise NotImplementedError("Replace this with your solution")