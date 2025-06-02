from highrise.models import User
from config.config import loggers
import logging


async def on_leave(bot, user: User) -> None:
    if loggers.leave:
        logging.info(f"User Left: {user.username}:{user.id}")
    await bot.highrise.chat(f"{user.username} Left the room!")
