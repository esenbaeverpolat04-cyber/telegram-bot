import os

# Telegram bot tokeningiz (Render Environment'dan o'qiydi)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8934424323:AAGbMfPqszB14-Q5yc79xG0n5kh5fFuvMWo")

# Sizning Telegram ID raqamingiz (Admin)
ADMIN_ID = int(os.getenv("ADMIN_ID", 6911619468))

# Ma'lumotlar bazasi fayli yo'li
DB_PATH = os.path.join(os.path.dirname(__file__), "database", "bot_database.db")