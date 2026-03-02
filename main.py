import asyncio
import logging

from aiogram import Bot, Dispatcher

from config_reader import config
from db import create_table
from handlers import router as handlers_router
from keyboards import router as keyboards_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()


async def main() -> None:
    dp.include_router(handlers_router)
    dp.include_router(keyboards_router)

    await create_table()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
