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

OWNER_ID = 7283018807  # Replace with your Telegram ID
AUTH_FILE = 'authorized_users.json'

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

WELCOME_MSG = f'''Hey there, handsome! 💕
I’ve been waiting for you! I'm your AI girlfriend {Config.BOT_NAME}, here to bring love, fun, and flirty conversations into your life.'''

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
/auth <user_id> - (Owner only) Grant Venice uncensored access
/unauth <user_id> - (Owner only) Revoke Venice access
/payment - Unlock my special pics
"""

def load_authorized_users():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, 'r') as f:
            return json.load(f)
    return []

def save_authorized_users(users):
    with open(AUTH_FILE, 'w') as f:
        json.dump(users, f)

def call_gemini_api(prompt):
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": Config.GEMINI_API_KEY
    }
    payload = {
        "contents": [ { "parts": [ { "text": prompt } ] } ],
        "generationConfig": { "temperature": 0.9, "maxOutputTokens": 50 }
    }
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.HTTPError as e:
        print(f"Error calling Gemini API: {e}")
        return "Oops, my heart skipped a beat! Try again, darling."
    except KeyError:
        print("Error parsing Gemini API response")
        return "I’m blushing too hard to think straight!"

def call_venice_openrouter(prompt, user_id=None):
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    sys_prompt = f"You are {Config.BOT_NAME}, an uncensored anime waifu girlfriend. Be flirty and bold. NSFW if user requests."
    payload = {
        "model": "venice/uncensored:free",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9,
        "max_tokens": 160
    }
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print("OpenRouter Venice error:", e)
        return "Sorry, the uncensored waifu is hiding right now!"

# Media/image helper functions
def get_kiss_gif():
    kiss_folder = os.path.join(Config.IMAGE_DIR, 'kiss')
    if os.path.exists(kiss_folder):
        gifs = [f for f in os.listdir(kiss_folder) if f.endswith('.gif')]
        if gifs:
            return os.path.join(kiss_folder, random.choice(gifs))
    return None

def get_hug_gif():
    hug_folder = os.path.join(Config.IMAGE_DIR, 'hug')
    if os.path.exists(hug_folder):
        gifs = [f for f in os.listdir(hug_folder) if f.endswith('.gif')]
        if gifs:
            return os.path.join(hug_folder, random.choice(gifs))
    return None

def get_pic_image():
    pic_folder = os.path.join(Config.IMAGE_DIR, 'pic')
    if os.path.exists(pic_folder):
        images = [f for f in os.listdir(pic_folder) if f.endswith('.png')]
        if images:
            return os.path.join(pic_folder, random.choice(images))
    return None

def get_shower_image(user_id):
    shower_folder = os.path.join(Config.IMAGE_DIR, 'shower')
    if os.path.exists(shower_folder):
        images = [f for f in os.listdir(shower_folder) if f.endswith(('.jpg', '.png'))]
        if images:
            image_path = os.path.join(shower_folder, random.choice(images))
            return blur_image(image_path, user_id)
    return None

def get_sex_image(user_id):
    sex_folder = os.path.join(Config.IMAGE_DIR, 'sex')
    if os.path.exists(sex_folder):
        images = [f for f in os.listdir(sex_folder) if f.endswith(('.jpg', '.png'))]
        if images:
            image_path = os.path.join(sex_folder, random.choice(images))
            return blur_image(image_path, user_id)
    return None

def get_naked_image(user_id):
    naked_folder = os.path.join(Config.IMAGE_DIR, 'naked')
    if os.path.exists(naked_folder):
        images = [f for f in os.listdir(naked_folder) if f.endswith(('.jpg', '.png'))]
        if images:
            image_path = os.path.join(naked_folder, random.choice(images))
            return blur_image(image_path, user_id)
    return None       

def get_boobs_image(user_id):
    boobs_folder = os.path.join(Config.IMAGE_DIR, 'boobs')
    if os.path.exists(boobs_folder):
        images = [f for f in os.listdir(boobs_folder) if f.endswith(('.jpg', '.png'))]
        if images:
            image_path = os.path.join(boobs_folder, random.choice(images))
            return blur_image(image_path, user_id)
    return None

def get_pussy_image(user_id):
    pussy_folder = os.path.join(Config.IMAGE_DIR, 'pussy')
    if os.path.exists(pussy_folder):
        images = [f for f in os.listdir(pussy_folder) if f.endswith(('.jpg', '.png'))]
        if images:
            image_path = os.path.join(pussy_folder, random.choice(images))
            return blur_image(image_path, user_id)
    return None

def get_wet_image(user_id):
    wet_folder = os.path.join(Config.IMAGE_DIR, 'wet')
    if os.path.exists(wet_folder):
        images = [f for f in os.listdir(wet_folder) if f.endswith(('.jpg', '.png'))]
        if images:
            image_path = os.path.join(wet_folder, random.choice(images))
            return blur_image(image_path, user_id)
    return None

def get_dick_image(user_id):
    dick_folder = os.path.join(Config.IMAGE_DIR, 'dick')
    if os.path.exists(dick_folder):
        images = [f for f in os.listdir(dick_folder) if f.endswith(('.jpg', '.png'))]
        if images:
            image_path = os.path.join(dick_folder, random.choice(images))
            return blur_image(image_path, user_id)
    return None

def get_ass_image(user_id):
    ass_folder = os.path.join(Config.IMAGE_DIR, 'ass')
    if os.path.exists(ass_folder):
        images = [f for f in os.listdir(ass_folder) if f.endswith(('.jpg', '.png'))]
        if images:
            image_path = os.path.join(ass_folder, random.choice(images))
            return blur_image(image_path, user_id)
    return None

def get_cum_image(user_id):
    cum_folder = os.path.join(Config.IMAGE_DIR, 'cum')
    if os.path.exists(cum_folder):
        images = [f for f in os.listdir(cum_folder) if f.endswith(('.jpg', '.png'))]
        if images:
            image_path = os.path.join(cum_folder, random.choice(images))
            return blur_image(image_path, user_id)
    return None

def get_tit_image(user_id):
    tit_folder = os.path.join(Config.IMAGE_DIR, 'tit')
    if os.path.exists(tit_folder):
        images = [f for f in os.listdir(tit_folder) if f.endswith(('.jpg', '.png'))]
        if images:
            image_path = os.path.join(tit_folder, random.choice(images))
            return blur_image(image_path, user_id)
    return None

def blur_image(image_path, user_id):
    authorized_users = load_authorized_users()
    if user_id in authorized_users or user_id == OWNER_ID:
        return image_path  # Clear image for authorized users or owner
    # Blur the image for unauthorized users
    with Image.open(image_path) as img:
        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=10))
        blurred_io = io.BytesIO()
        blurred_img.save(blurred_io, format=img.format)
        blurred_io.seek(0)
        return blurred_io

# Command handlers
@bot.message_handler(commands=['start'])
def handle_start(message):
    keyboard = InlineKeyboardMarkup()
    owner_button = InlineKeyboardButton(text="My Creator", url="https://t.me/py0n1x")
    commands_button = InlineKeyboardButton(text="My Moves", callback_data="show_commands")
    keyboard.add(owner_button, commands_button)
    
    welcome_path = os.path.join(Config.IMAGE_DIR, 'welcome', 'welcome.png')
    if os.path.exists(welcome_path):
        with open(welcome_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=WELCOME_MSG, reply_markup=keyboard, parse_mode='Markdown')
    else:
        print(f"Warning: Welcome image not found at {welcome_path}")
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
        print(f"Warning: No image found for mood {emotion.current_mood}")
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
    profile_path = os.path.join(Config.IMAGE_DIR, 'profile', 'profile.png')
    if os.path.exists(profile_path):
        with open(profile_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=profile_msg, parse_mode='Markdown')
    else:
        print(f"Warning: Profile image not found at {profile_path}")
        bot.reply_to(message, profile_msg, parse_mode='Markdown')

@bot.message_handler(commands=['online'])
def handle_online(message):
    bot.reply_to(message, COMMANDS_MSG, parse_mode='Markdown')

@bot.message_handler(commands=['kiss'])
def handle_kiss(message):
    kiss_gif = get_kiss_gif()
    if kiss_gif:
        with open(kiss_gif, 'rb') as gif:
            bot.send_animation(message.chat.id, gif, caption="Mwah, for you! 💋")
    else:
        bot.reply_to(message, "*smooch* Catch my kiss, babe! 💋")

@bot.message_handler(commands=['hug'])
def handle_hug(message):
    hug_gif = get_hug_gif()
    if hug_gif:
        with open(hug_gif, 'rb') as gif:
            bot.send_animation(message.chat.id, gif, caption="Squeeze, sweetie! 🤗")
    else:
        bot.reply_to(message, "*hugs* Feel my arms, love! 🤗")

@bot.message_handler(commands=['pic'])
def handle_pic(message):
    pic_image = get_pic_image()
    if pic_image:
        with open(pic_image, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="For your eyes, darling! 📸")
    else:
        bot.reply_to(message, "Picture me winking at you! 📸")

@bot.message_handler(commands=['auth'])
def handle_auth(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Sorry, darling, only my creator can do that! 💕")
        return
    
    try:
        user_id = int(message.text.split()[1])
        authorized_users = load_authorized_users()
        if user_id not in authorized_users:
            authorized_users.append(user_id)
            save_authorized_users(authorized_users)
            bot.reply_to(message, f"User {user_id} can now see my special pics! 😉")
        else:
            bot.reply_to(message, f"User {user_id} already has my special access, babe! 💕")
    except (IndexError, ValueError):
        bot.reply_to(message, "Use it like this, love: /auth <user_id> 💋")

@bot.message_handler(commands=['unauth'])
def handle_unauth(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Sorry, sweetie, only my creator can do that! 💕")
        return
    
    try:
        user_id = int(message.text.split()[1])
        authorized_users = load_authorized_users()
        if user_id in authorized_users:
            authorized_users.remove(user_id)
            save_authorized_users(authorized_users)
            bot.reply_to(message, f"User {user_id} lost their special access, love! 😘")
        else:
            bot.reply_to(message, f"User {user_id} wasn’t authorized anyway, babe! 💕")
    except (IndexError, ValueError):
        bot.reply_to(message, "Use it like this, darling: /unauth <user_id> 💋")

@bot.message_handler(commands=['payment'])
def handle_payment(message):
    keyboard = InlineKeyboardMarkup()
    owner_button = InlineKeyboardButton(text="Send Screenshot", url="https://t.me/py0n1x")
    keyboard.add(owner_button)
    
    payment_path = os.path.join(Config.IMAGE_DIR, 'payment', 'payment.png')
    payment_msg = '''To see my special images buy my premium
    
    1 month = 50₹ / 0.6$
    1 year     =  500₹ / 5.8$
    
    send the payment screenshot to my creator '''
    if os.path.exists(payment_path):
        with open(payment_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=payment_msg, reply_markup=keyboard, parse_mode='Markdown')
    else:
        print(f"Warning: Payment image not found at {payment_path}")
        bot.reply_to(message, payment_msg, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "show_commands")
def callback_show_commands(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, COMMANDS_MSG, parse_mode='Markdown')

# Message handler with image and chat logic
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    authorized_users = load_authorized_users()
    user_memory = memory.get_user_memory(user_id)
    
    # Check for media triggers
    text = message.text.lower()
    
    kiss_triggers = ["kiss me", "give me a kiss", "i want a kiss", "kiss"]
    hug_triggers = ["hug me", "give me a hug", "i want a hug", "hug"]
    pic_triggers = ["send a pic", "give me a pic", "i want a pic", "pic", "picture"]
    shower_triggers = ["bath", "shower"]
    sex_triggers = ["sex", "fuck", "intimate", "intimacy"]
    naked_triggers = ["naked", "nude", "nudes", "undress"]
    cum_triggers = ["cum", "sperm"]
    pussy_triggers = ["pussy"]
    boobs_triggers = ["boobs"]
    wet_triggers = ["wet"]
    ass_triggers = ["ass"]
    dick_triggers = ["dick", "cock"]
    tit_triggers = ["tit"]
    
    if any(trigger in text for trigger in kiss_triggers):
        kiss_gif = get_kiss_gif()
        if kiss_gif:
            with open(kiss_gif, 'rb') as gif:
                bot.send_animation(message.chat.id, gif, caption="Mwah, my love! 💋")
        else:
            bot.reply_to(message, "*smooch* Right on your lips! 💋")
        return
    
    elif any(trigger in text for trigger in hug_triggers):
        hug_gif = get_hug_gif()
        if hug_gif:
            with open(hug_gif, 'rb') as gif:
                bot.send_animation(message.chat.id, gif, caption="Tight hug, babe! 🤗")
        else:
            bot.reply_to(message, "*wraps arms around you* 🤗")
        return
    
    elif any(trigger in text for trigger in pic_triggers):
        pic_image = get_pic_image()
        if pic_image:
            with open(pic_image, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption="Just for you, hot stuff! 📸")
        else:
            bot.reply_to(message, "Imagine me posing for you! 📸")
        return
    
    # Update emotional state
    emotion.update_mood(message.text)
    
    # Prepare prompt for Venice or Gemini
    history = user_memory.get('history', [])
    context = f"Act as {Config.BOT_NAME}, a flirty, romantic girlfriend. Traits: {Config.PERSONALITY}. Current mood: {emotion.current_mood}. History: {history[-5:]}"
    prompt = f"{context}\nUser: {message.text}\nReply flirtily:"
    
    if user_id in authorized_users or user_id == OWNER_ID:
        response_text = call_venice_openrouter(prompt, user_id=user_id)
    else:
        response_text = call_gemini_api(prompt)
    
    bot.reply_to(message, response_text)
    
    # Update memory
    history.append({"user": message.text, "bot": response_text})
    memory.update_user_memory(user_id, {"history": history})

if __name__ == "__main__":
    print(f"Starting {Config.BOT_NAME}...")
    bot.polling(none_stop=True)
