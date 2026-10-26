class SimpleCache:
    def __init__(self):
        raise NotImplementedError("Write your solution here")
    def set(self, key, value, now, ttl):
        # store (value, expiry) and return self
        raise NotImplementedError("Write your solution here")
    def get(self, key, now):
        # return value if present and now < expiry, else None (and drop if expired)
        raise NotImplementedError("Write your solution here")
    def get_or_set(self, key, loader, now, ttl):
        # return live cached value, else load+store+return
        raise NotImplementedError("Write your solution here")
    def invalidate(self, key):
        # remove key if present; return self
        raise NotImplementedError("Write your solution here")