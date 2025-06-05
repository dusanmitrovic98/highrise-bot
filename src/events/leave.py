import logging

from config.config import loggers
from highrise.models import User

from .dispatch_util import dispatch_event


async def on_leave(bot, user: User) -> None:
    if loggers.leave:
        logging.info(f"User Left: {user.username}:{user.id}")
    await bot.highrise.chat(f"{user.username} Left the room!")

    # Dispatch to all plugin/command on_leave handlers
    await dispatch_event(bot, "on_leave", user)
