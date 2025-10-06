import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.markdown import hbold

# --- ВАШИ НАСТРОЙКИ (вставьте сюда ваши данные) ---
# Токен теперь будем брать из переменных окружения, это безопаснее
TOKEN = os.environ.get("7598230437:AAERUTJ48urvWviIRLxlXhIqjGevNRRlFio", "7598230437:AAERUTJ48urvWviIRLxlXhIqjGevNRRlFio")
WEB_APP_URL = "https://udobnamebel.github.io/Catalog"
ABOUT_US_URL = "https://telegra.ph/O-nas-Mebel-Udobna-02-24"
CONTACTS_URL = "https://taplink.cc/udobnamebel"

# URL для вебхука, который сгенерирует Vercel
VERCEL_URL = os.environ.get("VERCEL_URL")
WEBHOOK_PATH = f"/api/webhook"
WEBHOOK_URL = f"https://{VERCEL_URL}{WEBHOOK_PATH}"
# ----------------------------------------------------

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """Обработчик, который будет вызываться при команде /start."""
    
    # Создаем кнопки
    keyboard = [
        [types.KeyboardButton(text="Каталог 📖", web_app=WebAppInfo(url=WEB_APP_URL))],
        [types.KeyboardButton(text="О нас ℹ️", url=ABOUT_US_URL), types.KeyboardButton(text="Контакты 📞", url=CONTACTS_URL)],
    ]
    reply_markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    await message.answer(f"Пожалуйста, выберите нужный раздел, {hbold(message.from_user.full_name)}!", reply_markup=reply_markup)

# Эти функции нужны для установки и удаления вебхука при запуске/остановке
@dp.startup()
async def on_startup(bot: Bot) -> None:
    if VERCEL_URL: # Устанавливаем вебхук, только если мы на сервере Vercel
        await bot.set_webhook(WEBHOOK_URL)

@dp.shutdown()
async def on_shutdown(bot: Bot) -> None:
    if VERCEL_URL: # Удаляем вебхук при остановке
        await bot.delete_webhook()

# Эта функция будет "корнем" нашего веб-приложения на Vercel
# Она будет принимать обновления от Telegram и передавать их боту
async def handle_webhook(req):
    try:
        # Получаем обновление от Telegram
        update = types.Update.model_validate_json(await req.text(), context={"bot": bot})
        # Передаем его в диспетчер aiogram для обработки
        await dp.feed_update(bot=bot, update=update)
        return {"status": "ok"}
    except Exception as e:
        logging.error(f"Error handling webhook: {e}")
        return {"status": "error"}

# Функция для локального запуска (для тестов на вашем компьютере)
async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Если мы запускаем файл напрямую, используем long polling
    asyncio.run(main())