# emotion_engine.py
import random
from config import Config

class EmotionEngine:
    def __init__(self):
        self.current_mood = random.choice(Config.MOOD_STATES)
        self.mood_level = 0.5

    def update_mood(self, message_text):
        # Simple mood analysis based on message content
        positive_words = ['love', 'happy', 'great', 'awesome']
        negative_words = ['sad', 'bad', 'hate', 'terrible']
        
        text = message_text.lower()
        if any(word in text for word in positive_words):
            self.mood_level = min(1.0, self.mood_level + 0.1)
        elif any(word in text for word in negative_words):
            self.mood_level = max(0.0, self.mood_level - 0.1)

    def get_mood_response(self):
        mood_descriptions = {
            "happy": "I'm feeling wonderful today!",
            "sad": "I'm a bit down at the moment...",
            "excited": "I'm so thrilled right now!",
            "bored": "Feeling a bit restless today.",
            "affectionate": "Feeling extra loving today!"
        }
        return mood_descriptions[self.current_mood]