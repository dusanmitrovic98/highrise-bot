from highrise.models import User, Reaction
from config.config import loggers
import logging
from .dispatch_util import dispatch_event


async def on_reaction(bot, user: User, reaction: Reaction, receiver: User) -> None:
    if loggers.reactions:
        logging.info(f"{user.username} send {reaction} to {receiver.username}")

    # Dispatch to all plugin/command on_reaction handlers
    await dispatch_event(bot, "on_reaction", user, reaction, receiver)
