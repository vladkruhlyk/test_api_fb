
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests

# Your bot token
API_TOKEN = '8186839066:AAFbAkbYq51Nrw6IhsgpKENG9wvEOUPi_FU'
CHANNEL_URL = 'https://t.me/+gtIRQIKVvXdkYjdk'
WEBHOOK_URL = 'https://s5.apix-drive.com/web-hooks/37136/rylgmsbl'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Handler for the /start command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Create button with callback_data for tracking
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("Получить доступ", callback_data="get_access")
    markup.add(button)

    # Send message with the button
    await message.reply("Подпишись на наш канал и получай бесплатные сигналы", reply_markup=markup)

# Handler for the "Get Access" button press
@dp.callback_query_handler(lambda c: c.data == 'get_access')
async def process_callback_button(callback_query: types.CallbackQuery):
    # Send message with the channel link
    await bot.send_message(callback_query.from_user.id, f"Подпишись на наш канал: {CHANNEL_URL}")

    # Send user data to webhook
    requests.post(WEBHOOK_URL, json={"user_id": callback_query.from_user.id, "username": callback_query.from_user.username})

    # Confirm button press to user
    await callback_query.answer("Доступ предоставлен")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
