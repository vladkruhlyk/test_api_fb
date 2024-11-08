import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from flask import Flask
import json
import uuid
from datetime import datetime

# Telegram bot token and other constants
API_TOKEN = '7962440273:AAFil5umD5oL8_tPFqbivsUXv-iG5clW2XI'
CHANNEL_URL = 'https://t.me/+gtIRQIKVvXdkYjdk'
FB_ACCESS_TOKEN = 'EAAMrsBFmyrQBO4bYFxLabLzZAUwmi33ppD6Ef4CauaigAIfAmBVk4ZCZAFkZBuOo47yeXBSSMZBc2uwoS8rKo1ma0dNnHVlOFadyaBc4CeeGpI7vgPZC7Bok8dmUqP2dMZAZCwlZBQ1EVGZCf9kahhVWcLN4WwvFF84rN7WGrYRkZBoR6TrMZChQj905CYtQIdDZA0x64VQZDZD'
FB_PIXEL_ID = '2386094468412808'

# Webhook settings
WEBHOOK_PATH = f"/bot/{API_TOKEN}"
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.environ.get('PORT', 5000))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

app = Flask(__name__)

# Handler for /start command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Получить доступ", callback_data="get_access")
    markup.add(button)
    await message.reply("Подпишись на наш канал и получай бесплатные сигналы", reply_markup=markup)

# Function to send event to Facebook Conversion API
def send_fb_conversion(user_id, username):
    url = f'https://graph.facebook.com/v13.0/{FB_PIXEL_ID}/events'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "data": [
            {
                "event_name": "Lead",
                "event_time": int(datetime.now().timestamp()),
                "event_source_url": CHANNEL_URL,
                "user_data": {
                    "client_user_agent": "TelegramBot",
                    "external_id": str(user_id),
                    "fb_login_id": username
                },
                "action_source": "website",
                "event_id": str(uuid.uuid4())  # уникальный ID события
            }
        ],
        "access_token": FB_ACCESS_TOKEN
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.text

# Handler for "Get Access" button click
@dp.callback_query_handler(lambda c: c.data == 'get_access')
async def process_callback_button(callback_query: types.CallbackQuery):
    # Send message with the channel link
    await bot.send_message(callback_query.from_user.id, f"Подпишись на наш канал: {CHANNEL_URL}")

    # Send conversion event to Facebook API
    status_code, response_text = send_fb_conversion(callback_query.from_user.id, callback_query.from_user.username)
    if status_code == 200:
        print("Event sent to Facebook successfully.")
    else:
        print(f"Failed to send event to Facebook: {response_text}")

    await callback_query.answer("Доступ предоставлен")

@app.route('/')
def home():
    return "Bot is running"

# Setting up webhook
async def on_startup(dp):
    await bot.set_webhook(f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}")

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
