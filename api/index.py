import asyncio
from http.server import BaseHTTPRequestHandler
import json
from bot import dp, bot, TOKEN, WEBHOOK_URL  # Импортируем из нашего основного файла
from aiogram import types

class handler(BaseHTTPRequestHandler):
    async def do_POST(self):
        try:
            # Устанавливаем вебхук, если он еще не установлен
            current_webhook = await bot.get_webhook_info()
            if current_webhook.url != WEBHOOK_URL:
                await bot.set_webhook(url=WEBHOOK_URL)

            # Читаем данные, которые прислал Telegram
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            update = types.Update.model_validate(json.loads(post_body), context={"bot": bot})
            
            # Передаем обновление в диспетчер aiogram
            await dp.feed_update(bot=bot, update=update)

            self.send_response(200)
            self.end_headers()
        except Exception as e:
            print(f"Error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def do_GET(self):
        # Этот метод нужен, чтобы Vercel мог проверить, что сервис работает
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running!')

# Vercel будет вызывать эту функцию
async def main(request, response):
    server = handler(request, response, server=None)
    await server.do_POST()