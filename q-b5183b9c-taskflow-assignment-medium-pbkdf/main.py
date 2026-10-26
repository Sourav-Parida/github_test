import hashlib
import hmac

ITERATIONS = 100000

def hash_password(password, salt, iterations=ITERATIONS):
    # Return the password hash as a hex string.
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations
    )
    return hashed.hex()


def make_record(password, salt, iterations=ITERATIONS):
    # Return iterations$salt_hex$hash_hex.
    hash_hex = hash_password(password, salt, iterations)
    return f"{iterations}${salt.hex()}${hash_hex}"


def verify_password(password, record):
    #  Verify a password against a stored record.
    try:
        iterations_str, salt_hex, hash_hex = record.split('$')

        iterations = int(iterations_str)
        salt = bytes.fromhex(salt_hex)

        if iterations <= 0 or not salt:
            return False

        computed_hash = hash_password(password, salt, iterations)

        return hmac.compare_digest(computed_hash, hash_hex)

    except (ValueError, TypeError, AttributeError):
        return False