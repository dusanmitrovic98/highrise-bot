from highrise.models import User
from config.config import loggers
import logging
from .dispatch_util import dispatch_event

async def on_emote(bot, user: User, emote_id: str, receiver: User) -> None:
    if loggers.emotes:
        logging.info(f"User {user.username} sent {emote_id} to {receiver.username}")
    # Dispatch to all plugin/command on_emote handlers
    await dispatch_event(bot, "on_emote", user, emote_id, receiver)
