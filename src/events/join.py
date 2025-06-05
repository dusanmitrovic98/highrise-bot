from highrise.models import User
from config.config import loggers
import logging
from .dispatch_util import dispatch_event


async def on_join(bot, user: User) -> None:
    if loggers.joins:
        logging.info(f"User joined: {user.username}:{user.id}")
    await bot.highrise.chat(f"{user.username} Joined the room!")

    # Dispatch to all plugin/command on_join handlers
    await dispatch_event(bot, "on_join", user)
