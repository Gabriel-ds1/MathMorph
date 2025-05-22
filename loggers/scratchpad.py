# loggers/scratchpad.py

from collections import deque

class Scratchpad:
    def __init__(self, capacity=100):
        self.memory = deque(maxlen=capacity)

    def add(self, item):
        self.memory.append(item)

    def get_all(self):
        return list(self.memory)
    
    def latest(self, n=1):
        return list(self.memory)[-n:] if n <= len(self.memory) else list(self.memory)
    
    def clear(self):
        self.memory.clear()