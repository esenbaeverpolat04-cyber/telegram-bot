import asyncio
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.models import init_db

# Barcha routerlarni chaqirib olamiz
from handlers.user_handlers import router as user_router
from handlers.admin_handlers import admin_router
from handlers.admin_services import router as admin_services_router
from handlers.admin_users import router as admin_users_router

# Render uchun kichik web-server (port talabini qondirish uchun)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running 24/7!")
        
    def log_message(self, format, *args):
        pass # Loglarni to'ldirib yubormasligi uchun o'chirib qo'yildi

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

# Serverni alohida oqimda (thread) bot bilan birga ishga tushiramiz
threading.Thread(target=run_server, daemon=True).start()

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Ma'lumotlar bazasi va jadvallarni yaratamiz
    init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Admin routerlarini foydalanuvchi routeridan oldin ulaymiz
    dp.include_router(admin_router)
    dp.include_router(admin_services_router)
    dp.include_router(admin_users_router)
    dp.include_router(user_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi!")