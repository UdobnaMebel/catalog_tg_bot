import logging
import os
from telegram import Update, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes

# --- ВАШИ НАСТРОЙКИ ---
# Токен будем брать из переменных окружения на Render
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

WEB_APP_URL = "https://udobnamebel.github.io/Catalog"
ABOUT_US_URL = "https://telegra.ph/O-nas-Mebel-Udobna-02-24"
CONTACTS_URL = "https://taplink.cc/udobnamebel"
# ----------------------------------------------------

# Настройка логирования для отладки
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Функция, которая будет вызываться при команде /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [KeyboardButton("Каталог 📖", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton("О нас ℹ️", url=ABOUT_US_URL), KeyboardButton("Контакты 📞", url=CONTACTS_URL)],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Пожалуйста, выберите нужный раздел:",
        reply_markup=reply_markup
    )

# Функция для установки кнопки Menu
async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Перезапустить бота"),
    ])
    
    # Устанавливаем кнопку Menu слева внизу, которая открывает каталог
    await application.bot.set_chat_menu_button(
        menu_button=WebAppInfo(url=WEB_APP_URL)
    )

def main() -> None:
    """Основная функция для запуска бота."""
    if not TOKEN:
        logger.error("Токен не найден! Убедитесь, что переменная TELEGRAM_BOT_TOKEN установлена.")
        return

    application = Application.builder().token(TOKEN).post_init(post_init).build()
    application.add_handler(CommandHandler("start", start))
    
    logger.info("Бот запущен в режиме long polling...")
    application.run_polling()

if __name__ == "__main__":
    main()