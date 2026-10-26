def build_cache_key(entity, **filters):
    # 1. guard: if entity is not a non-empty string, return None
    # 2. if there are no filters, return entity
    # 3. build 'key=value' parts for each filter, SORTED by key
    # 4. join with '&' and return entity + ':' + joined
    raise NotImplementedError("Replace this with your solution")