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

# --- NEW: Venice API Function ---
def call_venice_openrouter(prompt, user_id=None):
    # OpenRouter's endpoint
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    sys_prompt = f"You are {Config.BOT_NAME}, an uncensored anime waifu girlfriend. Be flirty and bold. NSFW if user requests."
    payload = {
        "model": "venice/uncensored:free",  # This is the OpenRouter Venice uncensored model
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


# Initialize components
bot = telebot.TeleBot(Config.TELEGRAM_TOKEN)
memory = MemoryManager(Config.MEMORY_FILE)
emotion = EmotionEngine()
images = ImageHandler()

OWNER_ID = 7996439748  # Replace with your Telegram ID
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

# --- Auth commands ---
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
            bot.reply_to(message, f"{user_id} now has Venice uncensored chat access! 🦄")
        else:
            bot.reply_to(message, f"{user_id} already is Venice uncensored. 💕")
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
            bot.reply_to(message, f"{user_id} lost Venice uncensored chat access. 😘")
        else:
            bot.reply_to(message, f"{user_id} wasn’t authorized anyway, babe! 💕")
    except (IndexError, ValueError):
        bot.reply_to(message, "Use it like this, darling: /unauth <user_id> 💋")

# --- Main chat handler changes ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    authorized_users = load_authorized_users()
    user_memory = memory.get_user_memory(user_id)
    # [ ... image/gif triggers as before ... ]

    # Prepare prompt/context
    history = user_memory.get('history', [])
    context = f"Act as {Config.BOT_NAME}, a flirty, romantic girlfriend. Traits: {Config.PERSONALITY}. Current mood: {emotion.current_mood}. History: {history[-5:]}"
    prompt = f"{context}\nUser: {message.text}\nReply flirtily:"
    # --- Decision: Venice or Gemini ---
    if user_id in authorized_users or user_id == OWNER_ID:
        response_text = call_venice_openrouter(prompt, user_id=user_id)
    else:
        response_text = call_gemini_api(prompt)

    # [ ... send images/gifs/response as before ... ]
    bot.reply_to(message, response_text)
    # Update memory
    history.append({"user": message.text, "bot": response_text})
    memory.update_user_memory(user_id, {"history": history})

# [ ... rest of handlers stay unchanged ... ]

if __name__ == "__main__":
    print(f"Starting {Config.BOT_NAME}...")
    bot.polling(none_stop=True)
