import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.db import init_db_pool, close_db_pool
from handlers import owner, user

logging.basicConfig(level=logging.INFO)

# Render Web Service HTTP portni "tinglashini" talab qiladi (Background Worker
# bu hisobda mavjud emas). Shu sabab bot bilan bir qatorda soddagina health-check
# server ham ishga tushiriladi - u faqat Render'ning "ishlayapti" tekshiruvi uchun.
PORT = int(os.getenv("PORT", "10000"))


async def handle_health(request):
    return web.Response(text="Bot is running")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logging.info(f"Health-check server {PORT}-portda ishga tushdi")


async def start_bot():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    await init_db_pool()

    # MUHIM: owner router birinchi ro'yxatdan o'tishi kerak,
    # aks holda owner xabarlari user.py'dagi umumiy handlerga tushib qoladi
    dp.include_router(owner.router)
    dp.include_router(user.router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await close_db_pool()


async def main():
    # Ikkalasi ham bir vaqtda, parallel ishlaydi
    await asyncio.gather(
        start_web_server(),
        start_bot(),
    )


if __name__ == "__main__":
    asyncio.run(main())
