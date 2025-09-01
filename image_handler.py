import os
import random
from config import Config

class ImageHandler:
    def __init__(self):
        self.image_dir = Config.IMAGE_DIR

    def _get_random_image_from_folder(self, folder_name):
        folder_path = os.path.join(self.image_dir, folder_name)
        if os.path.exists(folder_path):
            images = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png', '.jpeg', '.gif'))]
            if images:
                return os.path.join(folder_path, random.choice(images))
        return None

    # Main folder getters matching your structure
    def get_kiss_gif(self): return self._get_random_image_from_folder("kiss")
    def get_hug_gif(self): return self._get_random_image_from_folder("hug")
    def get_pic_image(self): return self._get_random_image_from_folder("pic")
    def get_shower_image(self, user_id=None): return self._get_random_image_from_folder("shower")
    def get_sex_image(self, user_id=None): return self._get_random_image_from_folder("sex")
    def get_naked_image(self, user_id=None): return self._get_random_image_from_folder("naked")
    def get_boobs_image(self, user_id=None): return self._get_random_image_from_folder("boobs")
    def get_pussy_image(self, user_id=None): return self._get_random_image_from_folder("pussy")
    def get_wet_image(self, user_id=None): return self._get_random_image_from_folder("wet")
    def get_dick_image(self, user_id=None): return self._get_random_image_from_folder("dick")
    def get_ass_image(self, user_id=None): return self._get_random_image_from_folder("ass")
    def get_cum_image(self, user_id=None): return self._get_random_image_from_folder("cum")
    def get_tit_image(self, user_id=None): return self._get_random_image_from_folder("tit")

    # For moods, just use the folder name matching the mood
    def get_mood_image(self, mood): return self._get_random_image_from_folder(mood)
