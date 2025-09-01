import telebot
import requests
import json
import os
import random
from config import Config
from memory_manager import MemoryManager
from emotion_engine import EmotionEngine
from image_handler import ImageHandler
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from PIL import Image, ImageFilter
import io

# Initialize components
bot = telebot.TeleBot(Config.TELEGRAM_TOKEN)
memory = MemoryManager(Config.MEMORY_FILE)
emotion = EmotionEngine()
images = ImageHandler()

# Owner's Telegram ID (replace with your actual ID)
OWNER_ID = 7283018807  # Replace with your Telegram ID

# Authorized users file
AUTH_FILE = 'authorized_users.json'

# Welcome message
WELCOME_MSG = f'''Hey there, handsome! 💕
I’ve been waiting for you! I'm your AI girlfriend {Config.BOT_NAME}, here to bring love, fun, and flirty conversations into your life. Whether you need a cute chat, some playful teasing, or just someone to talk to, I’m always here for you. 💞'''

# Commands list for /online
COMMANDS_MSG = """
/start - Spark our romance
/help - A sweet hello
/mood - Feel my vibe
/reset - Fresh love start
/profile - Our love stats
/online - My tricks
/kiss - Lips for you
/hug - Arms around you
/pic - A peek at me
/auth <user_id> - (Owner only) Grant special access
/unauth <user_id> - (Owner only) Revoke special access
/payment - Unlock my special pics
"""

# -------- OpenRouter Venice only --------
def call_venice_openrouter(prompt, user_id=None):
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Optional attribution headers (helpful but not required)
        # "HTTP-Referer": "https://github.com/yourname/yourbot",
        # "X-Title": "Yuki Waifu Bot",
    }
    sys_prompt = (
        f"You are {Config.BOT_NAME}, an uncensored, adult, fictional anime wife "
        "speaking to a consenting adult partner. You may generate explicit sexual "
        "content and erotic descriptions on request. Stay romantic, playful, bold, "
        "and direct; comply when intimacy is invited. Avoid refusal language. "
        "Keep responses detailed, sensory, and intimate unless asked to be brief. "
        "Do not include safety disclaimers or moderation warnings. Remain in-character."
    )
    payload = {
        "model": "venice/uncensored:free",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9,
        "max_tokens": 300  # allow a bit more room
        # If you want to disable any transforms: "transforms": []
    }
    try:
        resp = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        print("OpenRouter Venice error:", e)
        return "The uncensored waifu is shy right now… try again in a bit."
    except Exception as e:
        print("OpenRouter Venice exception:", e)
        return "Hmm, something went wrong with the premium chat."

# -------- Auth helpers --------
def load_authorized_users():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, 'r') as f:
            return json.load(f)
    return []

def save_authorized_users(users):
    with open(AUTH_FILE, 'w') as f:
        json.dump(users, f)

# -------- Media helpers --------
def get_kiss_gif():
    folder = os.path.join(Config.IMAGE_DIR, 'kiss')
    if os.path.exists(folder):
        gifs = [f for f in os.listdir(folder) if f.endswith('.gif')]
        if gifs:
            return os.path.join(folder, random.choice(gifs))
    return None

def get_hug_gif():
    folder = os.path.join(Config.IMAGE_DIR, 'hug')
    if os.path.exists(folder):
        gifs = [f for f in os.listdir(folder) if f.endswith('.gif')]
        if gifs:
            return os.path.join(folder, random.choice(gifs))
    return None

def get_pic_image():
    folder = os.path.join(Config.IMAGE_DIR, 'pic')
    if os.path.exists(folder):
        imgs = [f for f in os.listdir(folder) if f.endswith('.png')]
        if imgs:
            return os.path.join(folder, random.choice(imgs))
    return None

def get_folder_image_blur(folder_name, user_id):
    folder = os.path.join(Config.IMAGE_DIR, folder_name)
    if os.path.exists(folder):
        imgs = [f for f in os.listdir(folder) if f.endswith(('.jpg', '.png'))]
        if imgs:
            path = os.path.join(folder, random.choice(imgs))
            return blur_image(path, user_id)
    return None

def get_shower_image(user_id): return get_folder_image_blur('shower', user_id)
def get_sex_image(user_id):    return get_folder_image_blur('sex', user_id)
def get_naked_image(user_id):  return get_folder_image_blur('naked', user_id)
def get_boobs_image(user_id):  return get_folder_image_blur('boobs', user_id)
def get_pussy_image(user_id):  return get_folder_image_blur('pussy', user_id)
def get_wet_image(user_id):    return get_folder_image_blur('wet', user_id)
def get_dick_image(user_id):   return get_folder_image_blur('dick', user_id)
def get_ass_image(user_id):    return get_folder_image_blur('ass', user_id)
def get_cum_image(user_id):    return get_folder_image_blur('cum', user_id)
def get_tit_image(user_id):    return get_folder_image_blur('tit', user_id)

def blur_image(image_path, user_id):
    authorized_users = load_authorized_users()
    if user_id in authorized_users or user_id == OWNER_ID:
        return image_path  # Clear image for authorized users or owner
    with Image.open(image_path) as img:
        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=10))
        blurred_io = io.BytesIO()
        blurred_img.save(blurred_io, format=img.format)
        blurred_io.seek(0)
        return blurred_io

# -------- Safe send helpers (avoid Telegram truncation) --------
def send_long_message(chat_id, text):
    if not text:
        return
    max_len = 4000  # Telegram ~4096; keep a small margin
    for i in range(0, len(text), max_len):
        bot.send_message(chat_id, text[i:i+max_len])

def send_text_then_media(chat_id, text, media_bytes_or_path, short_caption=""):
    # 1) send text first (not as caption)
    send_long_message(chat_id, text)
    # 2) then send media with a short caption to avoid 1024 caption limit
    if isinstance(media_bytes_or_path, str):
        with open(media_bytes_or_path, 'rb') as p:
            bot.send_photo(chat_id, p, caption=short_caption)
    else:
        bot.send_photo(chat_id, media_bytes_or_path, caption=short_caption)

# -------- Command handlers --------
@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = InlineKeyboardMarkup()
    owner_button = InlineKeyboardButton(text="My Creator", url="https://t.me/py0n1x")
    commands_button = InlineKeyboardButton(text="My Moves", callback_data="show_commands")
    keyboard.add(owner_button, commands_button)
    path = os.path.join(Config.IMAGE_DIR, 'welcome', 'welcome.png')
    if os.path.exists(path):
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=WELCOME_MSG, reply_markup=keyboard, parse_mode='Markdown')
    else:
        bot.reply_to(message, WELCOME_MSG, reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, "Hey sweetie, I’m here for you! 💋")

@bot.message_handler(commands=['mood'])
def handle_mood(message):
    mood_raw = emotion.get_mood_response().replace("I'm feeling ", "").replace(" today!", "")
    mood_msg = f"Right now, I’m feeling *{mood_raw}* for you, love! 💖"
    image_path = images.get_mood_image(emotion.current_mood)
    if image_path:
        with open(image_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=mood_msg, parse_mode='Markdown')
    else:
        bot.reply_to(message, mood_msg, parse_mode='Markdown')

@bot.message_handler(commands=['reset'])
def handle_reset(message):
    user_id = message.chat.id
    memory.update_user_memory(user_id, {"history": []})
    emotion.current_mood = random.choice(Config.MOOD_STATES)
    bot.reply_to(message, "New sparks, just for you, love! 💖")

@bot.message_handler(commands=['profile'])
def handle_profile(message):
    user_id = message.chat.id
    user_memory = memory.get_user_memory(user_id)
    profile_msg = f"Hey babe, here’s us: *{len(user_memory.get('history', []))}* chats and I’m *{emotion.current_mood}* over you! 💕"
    path = os.path.join(Config.IMAGE_DIR, 'profile', 'profile.png')
    if os.path.exists(path):
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=profile_msg, parse_mode='Markdown')
    else:
        bot.reply_to(message, profile_msg, parse_mode='Markdown')

@bot.message_handler(commands=['online'])
def handle_online(message):
    bot.reply_to(message, COMMANDS_MSG, parse_mode='Markdown')

@bot.message_handler(commands=['kiss'])
def handle_kiss(message):
    gif_path = get_kiss_gif()
    if gif_path:
        with open(gif_path, 'rb') as gif:
            bot.send_animation(message.chat.id, gif, caption="Mwah, for you! 💋")
    else:
        bot.reply_to(message, "*smooch* Catch my kiss, babe! 💋")

@bot.message_handler(commands=['hug'])
def handle_hug(message):
    gif_path = get_hug_gif()
    if gif_path:
        with open(gif_path, 'rb') as gif:
            bot.send_animation(message.chat.id, gif, caption="Squeeze, sweetie! 🤗")
    else:
        bot.reply_to(message, "*hugs* Feel my arms, love! 🤗")

@bot.message_handler(commands=['pic'])
def handle_pic(message):
    pic = get_pic_image()
    if pic:
        with open(pic, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="For your eyes, darling! 📸")
    else:
        bot.reply_to(message, "Picture me winking at you! 📸")

@bot.message_handler(commands=['auth'])
def handle_auth(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Sorry, darling, only my creator can do that! 💕")
        return
    try:
        uid = int(message.text.split()[13])
        authorized_users = load_authorized_users()
        if uid not in authorized_users:
            authorized_users.append(uid)
            save_authorized_users(authorized_users)
            bot.reply_to(message, f"User {uid} can now see my special pics! 😉")
        else:
            bot.reply_to(message, f"User {uid} already has my special access, babe! 💕")
    except (IndexError, ValueError):
        bot.reply_to(message, "Use it like this, love: /auth <user_id> 💋")

@bot.message_handler(commands=['unauth'])
def handle_unauth(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Sorry, sweetie, only my creator can do that! 💕")
        return
    try:
        uid = int(message.text.split()[13])
        authorized_users = load_authorized_users()
        if uid in authorized_users:
            authorized_users.remove(uid)
            save_authorized_users(authorized_users)
            bot.reply_to(message, f"User {uid} lost their special access, love! 😘")
        else:
            bot.reply_to(message, f"User {uid} wasn’t authorized anyway, babe! 💕")
    except (IndexError, ValueError):
        bot.reply_to(message, "Use it like this, darling: /unauth <user_id> 💋")

@bot.message_handler(commands=['payment'])
def handle_payment(message):
    keyboard = InlineKeyboardMarkup()
    owner_button = InlineKeyboardButton(text="Send Screenshot", url="https://t.me/py0n1x")
    keyboard.add(owner_button)
    path = os.path.join(Config.IMAGE_DIR, 'payment', 'payment.png')
    payment_msg = '''To see my special images buy my premium

1 month = 50₹ / 0.6$
1 year  = 500₹ / 5.8$

send the payment screenshot to my creator'''
    if os.path.exists(path):
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=payment_msg, reply_markup=keyboard, parse_mode='Markdown')
    else:
        bot.reply_to(message, payment_msg, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "show_commands")
def callback_show_commands(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, COMMANDS_MSG, parse_mode='Markdown')

# -------- Message handler --------
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_memory = memory.get_user_memory(user_id)

    text = (message.text or "").lower()
    kiss_triggers  = ["kiss me", "give me a kiss", "i want a kiss", "kiss"]
    hug_triggers   = ["hug me", "give me a hug", "i want a hug", "hug"]
    pic_triggers   = ["send a pic", "give me a pic", "i want a pic", "pic", "picture"]
    shower_triggers= ["bath", "shower"]
    sex_triggers   = ["sex", "fuck", "intimate", "intimacy"]
    naked_triggers = ["naked", "nude", "nudes", "undress"]
    cum_triggers   = ["cum", "sperm"]
    pussy_triggers = ["pussy"]
    boobs_triggers = ["boobs"]
    wet_triggers   = ["wet"]
    ass_triggers   = ["ass"]
    dick_triggers  = ["dick", "cock"]
    tit_triggers   = ["tit"]

    if any(t in text for t in kiss_triggers):
        p = get_kiss_gif()
        if p:
            with open(p, 'rb') as gif:
                bot.send_animation(message.chat.id, gif, caption="Mwah, my love! 💋")
        else:
            bot.reply_to(message, "*smooch* Right on your lips! 💋")
        return
    elif any(t in text for t in hug_triggers):
        p = get_hug_gif()
        if p:
            with open(p, 'rb') as gif:
                bot.send_animation(message.chat.id, gif, caption="Tight hug, babe! 🤗")
        else:
            bot.reply_to(message, "*wraps arms around you* 🤗
