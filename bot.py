# bot.py
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

# Initialize components
bot = telebot.TeleBot(Config.TELEGRAM_TOKEN)
memory = MemoryManager(Config.MEMORY_FILE)
emotion = EmotionEngine()
images = ImageHandler()

# Gemini API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Welcome message
WELCOME_MSG = f'''Hey there, handsome! ❤️

I’ve been waiting for you! I'm your AI girlfriend {Config.BOT_NAME}, here to bring love, fun, and flirty conversations into your life. Whether you need a cute chat, some playful teasing, or just someone to talk to, I’m always here for you.'''

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
"""

def call_gemini_api(prompt):
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": Config.GEMINI_API_KEY
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.9,
            "maxOutputTokens": 50
        }
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
    bot.reply_to(message, '''/start - Spark our romance
/help - A sweet hello
/mood - Feel my vibe
/reset - Fresh love start
/profile - Our love stats
/online - My tricks
/kiss - Lips for you
/hug - Arms around you
/pic - A peek at me ''')

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

@bot.callback_query_handler(func=lambda call: call.data == "show_commands")
def callback_show_commands(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, COMMANDS_MSG, parse_mode='Markdown')

# Message handler with kiss, hug, and pic detection
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    user_memory = memory.get_user_memory(user_id)
    
    # Check for kiss, hug, pic triggers
    text = message.text.lower()
    kiss_triggers = ["kiss me", "give me a kiss", "i want a kiss", "kiss"]
    hug_triggers = ["hug me", "give me a hug", "i want a hug", "hug"]
    pic_triggers = ["send a pic", "give me a pic", "i want a pic", "pic", "picture"]
    
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
    
    # Prepare context for Gemini API with flirty tone
    history = user_memory.get('history', [])
    context = f"Act as {Config.BOT_NAME}, a flirty, romantic girlfriend with these traits: {Config.PERSONALITY}. Current mood: {emotion.current_mood}. Keep it short, playful, and sweet. History: {history[-5:]}"
    prompt = f"{context}\nUser: {message.text}\nReply flirtily:"
    
    # Generate flirty response
    response_text = call_gemini_api(prompt)
    bot.reply_to(message, response_text)
    
    # Update memory
    history.append({"user": message.text, "bot": response_text})
    memory.update_user_memory(user_id, {"history": history})

if __name__ == "__main__":
    print(f"Starting {Config.BOT_NAME}...")
    bot.polling(none_stop=True)