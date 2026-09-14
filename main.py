import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.models import init_db

# Barcha routerlarni chaqirib olamiz
from handlers.user_handlers import router as user_router
from handlers.admin_handlers import admin_router
from handlers.admin_services import router as admin_services_router
from handlers.admin_users import router as admin_users_router

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