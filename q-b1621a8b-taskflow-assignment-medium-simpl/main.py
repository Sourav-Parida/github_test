class SimpleCache:
    def __init__(self):
        self.cache = {}

    def set(self, key, value, now, ttl):
        # Store value and its expiry time
        self.cache[key] = (value, now + ttl)
        return self

    def get(self, key, now):
        # Return None if key does not exist
        if key not in self.cache:
            return None

        value, expiry = self.cache[key]

        # Expired when now >= expiry
        if now >= expiry:
            del self.cache[key]
            return None

        return value

    def get_or_set(self, key, loader, now, ttl):
        # Return cached value if it is still valid
        value = self.get(key, now)

        if value is not None:
            return value

        # Otherwise, load and cache the value
        value = loader()
        self.set(key, value, now, ttl)
        return value

    def invalidate(self, key):
        # Remove key if present
        self.cache.pop(key, None)
        return self