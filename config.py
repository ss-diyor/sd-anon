import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))  # sizning Telegram user ID'ingiz
DATABASE_URL = os.getenv("DATABASE_URL")  # Railway PostgreSQL avtomatik beradi
BOT_USERNAME = os.getenv("BOT_USERNAME", "")  # masalan: my_anon_bot (@ belgisisiz)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable topilmadi!")
if not OWNER_ID:
    raise RuntimeError("OWNER_ID environment variable topilmadi!")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable topilmadi!")
