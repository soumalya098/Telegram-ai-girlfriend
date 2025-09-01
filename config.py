import os

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    # Map user IDs to variable names (not the key itself for safety)
    USER_API_KEY_MAP = {
        7283018807: os.getenv("OPENROUTER_API_KEY_USER1", ""),
        987654321: os.getenv("OPENROUTER_API_KEY_USER2", ""),
        # add more user_id: os.getenv(...) pairs here
    }
    MEMORY_FILE = 'memory.json'
    IMAGE_DIR = 'images/'
    BOT_NAME = "Yuki"
    PERSONALITY = {
        "friendliness": 0.9,
        "humor": 0.7,
        "empathy": 0.85,
    }
    MOOD_STATES = ["happy", "sad", "excited", "bored", "affectionate"]
    MSG_LIMIT_FILE = "user_msg_limit.json"
