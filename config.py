# config.py
import os

class Config:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

    # File paths
    MEMORY_FILE = 'memory.json'
    IMAGE_DIR = 'images/'

    # Bot personality settings
    BOT_NAME = "Yuki"
    PERSONALITY = {
        "friendliness": 0.9,
        "humor": 0.7,
        "empathy": 0.85
    }

    # Emotional states
    MOOD_STATES = ["happy", "sad", "excited", "bored", "affectionate"]
