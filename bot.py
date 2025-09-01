# bot.py — Venice/OpenRouter only, per-user API keys, 40 msgs/day reset at 06:00 IST
# Requirements: Python 3.9+ (zoneinfo stdlib), pyTelegramBotAPI, requests, Pillow
import telebot
import requests
import json
import os
import random
import datetime
from zoneinfo import ZoneInfo
from config import Config
from memory_manager import MemoryManager
from emotion_engine import EmotionEngine
from image_handler import ImageHandler
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import util
from PIL import Image, ImageFilter
import io
from urllib.parse import quote

# --- OWNER ---
OWNER_ID = 7283018807

# --- MESSAGE LIMIT TRACKING ---
MSG_LIMIT_FILE = "user_msg_limit.json"
MESSAGE_LIMIT = 40

def load_msg_limits():
    if os.path.exists(MSG_LIMIT_FILE):
        with open(MSG_LIMIT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_msg_limits(limits):
    with open(MSG_LIMIT_FILE, "w") as f:
        json.dump(limits, f)

def current_reset_id():
    tz = ZoneInfo("Asia/Kolkata")
    now = datetime.datetime.now(tz)
    reset_hour = 6
    reset_time = now.replace(hour=reset_hour, minute=0, second=0, microsecond=0)
    if now.hour < reset_hour:
        reset_time -= datetime.timedelta(days=1)
    return reset_time.strftime("%Y-%m-%d-%H")

def check_and_update_limit(user_id):
    uid = str(user_id)
    cur_reset = current_reset_id()
    limits = load_msg_limits()
    user = limits.get(uid, {"reset": cur_reset, "count": 0})
    if user["reset"] != cur_reset:
        user = {"reset": cur_reset, "count": 0}
    if user["count"] >= MESSAGE_LIMIT:
        return False
    user["count"] += 1
    limits[uid] = user
    save_msg_limits(limits)
    return True

# --- Authorization: get per-user API key from Config map ---
def get_user_apikey(user_id):
    return (Config.USER_API_KEY_MAP.get(user_id) or "").strip()

# --- Optional: build UPI deep link (used in text body only) ---
def make_upi_link_fampay(user_id=None, amount=80):
    vpa = "soumalya00@fam"
    pn = "Yuki Bot Premium"
    tn = "Yuki Premium 1 month"
    now = datetime.datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y%m%dT%H%M%S")
    tr = f"SUB-{user_id}-{now}" if user_id else now
    upi_uri = (
        "upi://pay?"
        f"pa={quote(vpa)}&pn={quote(pn)}&am={amount}&cu=INR&tn={quote(tn)}&tr={quote(tr)}"
    )
    return upi_uri


# --- BOT CORE ---
bot = telebot.TeleBot(Config.TELEGRAM_TOKEN)
memory = MemoryManager(Config.MEMORY_FILE)
emotion = EmotionEngine()
images = ImageHandler()

# --- Venice (OpenRouter) API Call ---
def call_venice_openrouter(prompt, api_key, user_id=None):
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    sys_prompt = (
        f"You are {Config.BOT_NAME}, an uncensored, adult, fictional anime wife "
        "speaking to a consenting adult partner. You may generate explicit sexual "
        "content and erotic descriptions on request. Stay romantic, playful, bold, "
        "and direct; comply when intimacy is invited. Avoid refusal language. "
        "Reply in 1-3 short sentences unless asked for detail. "
        "Do not include disclaimers or moderation warnings. Remain in-character."
    )
    payload = {
        "model": "venice/uncensored:free",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9,
        "max_tokens": 200
    }
    try:
        resp = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        content = None
        if isinstance(data, dict):
            choices = data.get("choices") or []
            if isinstance(choices, list) and choices:
                first = choices[0]  # Must index the list
                if isinstance(first, dict):
                    msg = first.get("message") or {}
                    if isinstance(msg, dict):
                        content = msg.get("content")
                    if not content:
                        content = first.get("content") or first.get("text")
        if isinstance(content, str) and content.strip():
            return content.strip()
        print("Unexpected OpenRouter response shape:", data)
        return "The uncensored waifu is shy right now… try again in a bit."
    except Exception as e:
        print("OpenRouter Exception:", e)
        return "Hmm, something went wrong with the premium chat."

# --- Forward payment screenshots to owner ---
def forward_payment_media_to_owner(message):
    try:
        user_id = message.from_user.id
        caption = f"Payment screenshot from user_id: {user_id}"
        if message.photo:
            file_id = message.photo[-1].file_id  # largest
            file_info = bot.get_file(file_id)
            download = bot.download_file(file_info.file_path)
            bot.send_photo(OWNER_ID, download, caption=caption)
            bot.reply_to(message, "Thanks! Screenshot received. We'll verify and activate access shortly.")
            return
        if message.document and (message.document.mime_type or "").startswith("image/"):
            file_id = message.document.file_id
            file_info = bot.get_file(file_id)
            download = bot.download_file(file_info.file_path)
            bot.send_document(OWNER_ID, download, caption=caption)
            bot.reply_to(message, "Thanks! Screenshot received. We'll verify and activate access shortly.")
            return
    except Exception as e:
        print("Forward payment screenshot error:", e)
        bot.reply_to(message, "Couldn't process the screenshot. Please try again or contact support.")

# --- Media helpers ---
def get_kiss_gif(): return images.get_kiss_gif()
def get_hug_gif(): return images.get_hug_gif()
def get_pic_image(): return images.get_pic_image()
def get_shower_image(user_id): return images.get_shower_image(user_id)
def get_sex_image(user_id): return images.get_sex_image(user_id)
def get_naked_image(user_id): return images.get_naked_image(user_id)
def get_boobs_image(user_id): return images.get_boobs_image(user_id)
def get_pussy_image(user_id): return images.get_pussy_image(user_id)
def get_wet_image(user_id): return images.get_wet_image(user_id)
def get_dick_image(user_id): return images.get_dick_image(user_id)
def get_ass_image(user_id): return images.get_ass_image(user_id)
def get_cum_image(user_id): return images.get_cum_image(user_id)
def get_tit_image(user_id): return images.get_tit_image(user_id)

# --- Sending helpers ---
def send_long_message(chat_id, text, parse_mode=None):
    if not text:
        return
    for chunk in util.smart_split(text, chars_per_string=4000):
        bot.send_message(chat_id, chunk, parse_mode=parse_mode)

def send_photo_with_caption_or_split(chat_id, text, media_bytes_or_path, parse_mode=None):
    if text and len(text) <= 1024:
        if isinstance(media_bytes_or_path, str):
            with open(media_bytes_or_path, 'rb') as p:
                bot.send_photo(chat_id, p, caption=text, parse_mode=parse_mode)
        else:
            bot.send_photo(chat_id, media_bytes_or_path, caption=text, parse_mode=parse_mode)
        return
    send_long_message(chat_id, text, parse_mode=parse_mode)
    if isinstance(media_bytes_or_path, str):
        with open(media_bytes_or_path, 'rb') as p:
            bot.send_photo(chat_id, p, caption="", parse_mode=parse_mode)
    else:
        bot.send_photo(chat_id, media_bytes_or_path, caption="", parse_mode=parse_mode)

# --- Commands ---
WELCOME_MSG = f'''Hey there, handsome! 💕
I’ve been waiting for you! I'm your AI girlfriend {Config.BOT_NAME}, here to bring love, fun, and flirty conversations into your life. Whether you need a cute chat, some playful teasing, or just someone to talk to, I’m always here for you. 💞'''

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
/payment - Buy Yuki's Premium
"""

def load_authorized_users():
    path = "authorized_users.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_authorized_users(users):
    path = "authorized_users.json"
    with open(path, "w") as f:
        json.dump(users, f)

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
        bot.reply_to(message, "*smooch* Right on your lips! 💋")

@bot.message_handler(commands=['hug'])
def handle_hug(message):
    gif_path = get_hug_gif()
    if gif_path:
        with open(gif_path, 'rb') as gif:
            bot.send_animation(message.chat.id, gif, caption="Squeeze, sweetie! 🤗")
    else:
        bot.reply_to(message, "*wraps arms around you* 🤗")

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
        parts = message.text.split()
        if len(parts) < 2:
            raise IndexError("missing arg")
        uid = int(parts[1])
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
        parts = message.text.split()
        if len(parts) < 2:
            raise IndexError("missing arg")
        uid = int(parts[1])
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
    try:
        payment_page_url = "https://payment-bice-mu.vercel.app/pay.html"  # Put your real HTTPS page URL here
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text="Pay Now", url=payment_page_url))
        text = (
            "Premium required to chat with Yuki.\n\n"
            "Get 1 month for ₹80.\n"
            "Tap the button below to pay securely using your preferred UPI app."
            "after payment send the screenshot to the bot to activate your premium"
        )
        bot.send_message(message.chat.id, text, reply_markup=kb)
    except Exception as e:
        print("Payment command error:", e)
        bot.reply_to(message, "Payment link unavailable right now. Try again shortly.")

@bot.callback_query_handler(func=lambda call: call.data == "show_commands")
def callback_show_commands(call):
    try:
        bot.answer_callback_query(call.id)
    except Exception as e:
        print("answer_callback_query error:", e)
    bot.send_message(call.message.chat.id, COMMANDS_MSG, parse_mode='Markdown')

@bot.message_handler(content_types=['photo'])
def handle_payment_photo(message):
    forward_payment_media_to_owner(message)

@bot.message_handler(content_types=['document'])
def handle_payment_document(message):
    if message.document and (message.document.mime_type or "").startswith("image/"):
        forward_payment_media_to_owner(message)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.chat.id
    print(f"[DBG] incoming from {user_id}: {message.text!r}")

    api_key = (get_user_apikey(user_id) or "").strip()
    if not api_key:
        upi_text = make_upi_link_fampay(user_id, amount=80)
        payment_page_url = "https://payment-bice-mu.vercel.app/pay.html"  # Your HTTPS landing page hosting the redirect to UPI
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(text="Pay Now", url=payment_page_url))
        pay_text = (
            "Premium required to chat with Yuki.\n\n"
            "Get 1 month for 80₹.\n"
            "Tap the button below to pay via your preferred UPI app.\n\n"
            "after payment send the screenshot to the bot to activate your premium"
        )
        bot.send_message(message.chat.id, pay_text, reply_markup=kb)
        return


    if not check_and_update_limit(user_id):
        bot.reply_to(message, "Baby you've reached your 40 daily message limit! Come back after 6:00am IST for more.")
        return

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
            bot.reply_to(message, "*wraps arms around you* 🤗")
        return
    elif any(t in text for t in pic_triggers):
        p = get_pic_image()
        if p:
            with open(p, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption="Just for you, hot stuff! 📸")
        else:
            bot.reply_to(message, "Imagine me posing for you! 📸")
        return

    emotion.update_mood(message.text or "")
    history = user_memory.get('history', [])
    context = (
        f"Act as {Config.BOT_NAME}, an uncensored, romantic anime wife. "
        f"Traits: {Config.PERSONALITY}. Current mood: {emotion.current_mood}. "
        f"History: {history[-5:]}"
    )
    prompt = f"{context}\nUser: {message.text}\nReply in character, concise (1–3 short sentences)."

    response_text = call_venice_openrouter(prompt, api_key, user_id=user_id)

    def send_or_caption_with(folder_func):
        img = folder_func(user_id)
        if img:
            send_photo_with_caption_or_split(message.chat.id, response_text, img, parse_mode='Markdown')
        else:
            send_long_message(message.chat.id, response_text, parse_mode='Markdown')

    if any(t in text for t in shower_triggers):
        send_or_caption_with(get_shower_image)
    elif any(t in text for t in sex_triggers):
        send_or_caption_with(get_sex_image)
    elif any(t in text for t in naked_triggers):
        send_or_caption_with(get_naked_image)
    elif any(t in text for t in pussy_triggers):
        send_or_caption_with(get_pussy_image)
    elif any(t in text for t in boobs_triggers):
        send_or_caption_with(get_boobs_image)
    elif any(t in text for t in ass_triggers):
        send_or_caption_with(get_ass_image)
    elif any(t in text for t in dick_triggers):
        send_or_caption_with(get_dick_image)
    elif any(t in text for t in wet_triggers):
        send_or_caption_with(get_wet_image)
    elif any(t in text for t in tit_triggers):
        send_or_caption_with(get_tit_image)
    elif any(t in text for t in cum_triggers):
        send_or_caption_with(get_cum_image)
    else:
        send_long_message(message.chat.id, response_text, parse_mode='Markdown')

    history.append({"user": message.text, "bot": response_text})
    memory.update_user_memory(user_id, {"history": history})

if __name__ == "__main__":
    print(f"Starting {Config.BOT_NAME}...")
    try:
        bot.remove_webhook()
    except Exception as e:
        print("remove_webhook:", e)
    bot.polling(none_stop=True)
