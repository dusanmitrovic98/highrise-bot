from highrise.models import User
from config.config import loggers
import logging


async def on_join(bot, user: User) -> None:
    if loggers.joins:
        logging.info(f"User joined: {user.username}:{user.id}")
    await bot.highrise.chat(f"{user.username} Joined the room!")
