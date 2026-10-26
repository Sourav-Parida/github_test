def sanitize_tag(raw):
    """Return a safe TaskFlow tag slug from a raw user string."""
    if not isinstance(raw, str):
        return "untitled"

    result = ''.join(
        char for char in raw.strip()
        if ('a' <= char <= 'z') or
          ('A' <= char <= 'Z') or
          ('0' <= char <= '9') or
          char in '-_'
    )

    return result if result else "untitled"