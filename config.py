# config.py
import os

class Config:
    TELEGRAM_TOKEN = '7804430632:AAEHuJu6K2Fen85azPayBB00LjNLtaOoUCk'
    GEMINI_API_KEY = 'AIzaSyCX0kyWeiJOPv6npQSsBJE1nYQzAwpC8H0'
    
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