# image_handler.py
import os
import random
from config import Config

class ImageHandler:
    def __init__(self):
        self.image_dir = Config.IMAGE_DIR

    def get_mood_image(self, mood):
        mood_folder = os.path.join(self.image_dir, mood)
        if os.path.exists(mood_folder):
            images = [f for f in os.listdir(mood_folder) if f.endswith(('.jpg', '.png'))]
            if images:
                return os.path.join(mood_folder, random.choice(images))
        return None