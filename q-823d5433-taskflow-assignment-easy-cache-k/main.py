def build_cache_key(entity, **filters):
    if not isinstance(entity, str) or not entity:
        return None

    if not filters:
        return entity

    parts = [
        f"{key}={value}"
        for key, value in sorted(filters.items())
    ]

    return entity + ":" + "&".join(parts)