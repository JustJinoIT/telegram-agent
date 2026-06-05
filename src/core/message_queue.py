"""telegram-agent 메시지 큐 (Phase 1)"""
import asyncio
from collections import deque

class MessageQueue:
    def __init__(self, max_size: int = 100):
        self.queue = deque(maxlen=max_size)
    
    async def enqueue(self, message: dict):
        self.queue.append(message)
    
    async def process_batch(self, batch_size: int = 10):
        batch = []
        while len(batch) < batch_size and self.queue:
            batch.append(self.queue.popleft())
        return batch
