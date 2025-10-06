import asyncio
import logging
import os
import json
from http.server import BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.markdown import hbold

# --- ВАШИ НАСТРОЙКИ (ВСЕ В ОДНОМ МЕСТЕ) ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEB_APP_URL = "https://udobnamebel.github.io/Catalog"
ABOUT_US_URL = "https://telegra.ph/O-nas-Mebel-Udobna-02-24"
CONTACTS_URL = "https://taplink.cc/udobnamebel"

# URL для вебхука, который сгенерирует Vercel
VERCEL_URL = os.environ.get("VERCEL_URL")
# Убедимся, что VERCEL_URL не пустой, чтобы избежать ошибок
if VERCEL_URL:
    WEBHOOK_PATH = f"/api/" # Vercel направляет запросы к index.py в этой папке
    WEBHOOK_URL = f"https://{VERCEL_URL}{WEBHOOK_PATH}"
else:
    WEBHOOK_URL = "" # Пусто, если запускаем локально
# ----------------------------------------------------

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    keyboard = [
        [types.KeyboardButton(text="Каталог 📖", web_app=WebAppInfo(url=WEB_APP_URL))],
        [types.KeyboardButton(text="О нас ℹ️", url=ABOUT_US_URL), types.KeyboardButton(text="Контакты 📞", url=CONTACTS_URL)],
    ]
    reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer(f"Пожалуйста, выберите нужный раздел, {hbold(message.from_user.full_name)}!", reply_markup=reply_markup)

# "Точка входа" для Vercel
class handler(BaseHTTPRequestHandler):
    async def do_POST(self):
        try:
            # Устанавливаем вебхук при первом вызове, если нужно
            current_webhook = await bot.get_webhook_info()
            if current_webhook.url != WEBHOOK_URL and VERCEL_URL:
                await bot.set_webhook(url=WEBHOOK_URL)

            # Читаем данные, которые прислал Telegram
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            
            # Создаем объект Update и передаем его в диспетчер
            update = types.Update.model_validate(json.loads(post_body), context={"bot": bot})
            await dp.feed_update(bot=bot, update=update)

            # Отвечаем Telegram, что все в порядке
            self.send_response(200)
            self.end_headers()
        except Exception as e:
            logging.error(f"Error handling webhook: {e}")
            self.send_response(500)
            self.end_headers()
    
    # Этот метод вызывается, когда Vercel обращается к нашему URL напрямую
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running and webhook is set up if deployed on Vercel.')

# Vercel будет вызывать эту асинхронную функцию
async def main(request, response):
    server = handler(request, response, server=None)
    await server.do_POST()