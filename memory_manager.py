# memory_manager.py
import json
import os

class MemoryManager:
    def __init__(self, memory_file):
        self.memory_file = memory_file
        self.memory = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {}

    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)

    def update_user_memory(self, user_id, data):
        if str(user_id) not in self.memory:
            self.memory[str(user_id)] = {}
        self.memory[str(user_id)].update(data)
        self.save_memory()

    def get_user_memory(self, user_id):
        return self.memory.get(str(user_id), {})