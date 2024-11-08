import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import json
import uuid
from datetime import datetime
from flask import Flask

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Telegram и Facebook API токены и ID пикселя
API_TOKEN = '8186839066:AAFbAkbYq51Nrw6IhsgpKENG9wvEOUPi_FU'
CHANNEL_URL = 'https://t.me/+gtIRQIKVvXdkYjdk'
FB_ACCESS_TOKEN = 'EAAMrsBFmyrQBO3xueGMEY5cbzcUh4kJQ7RLZBOy9TK4gZCOKzCnvr2xvUz8tkQ8Bb7mZB6YZBcL6Bz8i6uU0kV50F1GPAD3PrFYWkRhhSksJjrQJ9J6nEMwSxtMZBaU6tNoAcF4S3IgfE6kugPBQ2fZAZB8byFw0KvSA3Qu2S6rfn0WIQhZAV3PugxWZCQwNeZBeXzQgZDZD'
FB_PIXEL_ID = '2386094468412808'

# Параметры вебхука
WEBHOOK_PATH = f"/bot/{API_TOKEN}"
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.environ.get('PORT', 5000))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

app = Flask(__name__)

# Логирование старта
logger.info("Bot is starting...")

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    logger.info(f"Received /start command from {message.from_user.id} ({message.from_user.username})")
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Получить доступ", callback_data="get_access")
    markup.add(button)
    await message.reply("Подпишись на наш канал и получай бесплатные сигналы", reply_markup=markup)

# Функция для отправки события в Facebook Conversion API
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
                "event_id": str(uuid.uuid4())
            }
        ],
        "access_token": FB_ACCESS_TOKEN
    }
    response = requests.post(url, headers=headers, json=data)
    logger.info(f"Sent event to Facebook for user {user_id} ({username}): Status {response.status_code}, Response {response.text}")
    return response.status_code, response.text

# Обработчик нажатия на кнопку "Получить доступ"
@dp.callback_query_handler(lambda c: c.data == 'get_access')
async def process_callback_button(callback_query: types.CallbackQuery):
    logger.info(f"User {callback_query.from_user.id} ({callback_query.from_user.username}) clicked 'Get Access'")
    await bot.send_message(callback_query.from_user.id, f"Подпишись на наш канал: {CHANNEL_URL}")

    # Отправка события в Facebook API и логирование
    status_code, response_text = send_fb_conversion(callback_query.from_user.id, callback_query.from_user.username)
    if status_code == 200:
        logger.info("Event sent to Facebook successfully.")
    else:
        logger.error(f"Failed to send event to Facebook: {response_text}")

    await callback_query.answer("Доступ предоставлен")

@app.route('/')
def home():
    return "Bot is running"

# Настройка вебхука
async def on_startup(dp):
    await bot.set_webhook(f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}")
    logger.info("Webhook has been set.")

async def on_shutdown(dp):
    await bot.delete_webhook()
    logger.info("Webhook has been removed.")

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
