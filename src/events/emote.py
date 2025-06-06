import logging

from config.config import loggers
from highrise.models import User

from .dispatch_util import dispatch_event


async def on_emote(bot, user: User, emote_id: str, receiver: User) -> None:
    await dispatch_event(bot, "on_emote", user, emote_id, receiver)
