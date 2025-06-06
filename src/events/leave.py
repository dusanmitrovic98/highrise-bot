import logging

from config.config import loggers
from highrise.models import User

from .dispatch_util import dispatch_event


async def on_leave(bot, user: User) -> None:
    await bot.highrise.chat(f"{user.username} Left the room!")
    await dispatch_event(bot, "on_leave", user)
