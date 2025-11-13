import time

class SeenStore:
    def __init__(self, ttl=3600):
        self.ttl = ttl
        self.db = {}

    def already_seen(self, uid):
        now = time.time()
        # cleanup
        for k, t in list(self.db.items()):
            if now - t > self.ttl:
                self.db.pop(k, None)
        # check
        if uid in self.db:
            return True
        self.db[uid] = now
        return False