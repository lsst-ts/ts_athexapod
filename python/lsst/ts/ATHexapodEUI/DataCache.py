
import time

class DataCache:
    def __init__(self, initialValue = None):
        self.value = initialValue
        self.updated = initialValue is not None
        self.lastUpdated = time.time()

    def set(self, value):
        self.value = value
        self.updated = True
        self.lastUpdated = time.time()

    def hasBeenUpdated(self):
        updated = self.updated and self.value is not None
        self.updated = False
        return updated
    
    def get(self):
        return self.value

    def getTimeOfLastUpdate(self):
        return self.lastUpdated

    def getTimeSinceLastUpdate(self):
        return time.time() - self.lastUpdated