import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from flask import Flask

API_TOKEN = '8186839066:AAFbAkbYq51Nrw6IhsgpKENG9wvEOUPi_FU'
CHANNEL_URL = 'https://t.me/+gtIRQIKVvXdkYjdk'
WEBHOOK_URL = 'https://hooks.zapier.com/hooks/catch/13255128/2586sui/'

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

# Handler for "Get Access" button click
@dp.callback_query_handler(lambda c: c.data == 'get_access')
async def process_callback_button(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, f"Подпишись на наш канал: {CHANNEL_URL}")
    requests.post(WEBHOOK_URL, json={"user_id": callback_query.from_user.id, "username": callback_query.from_user.username})
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
