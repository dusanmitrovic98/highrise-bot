from highrise.models import User, Reaction
from config.config import loggers
import logging


async def on_reaction(bot, user: User, reaction: Reaction, receiver: User) -> None:
    if loggers.reactions:
        logging.info(f"{user.username} send {reaction} to {receiver.username}")

    # Dispatch to all plugin/command on_reaction handlers
    for command in getattr(bot, 'commands', []):
        for handler in getattr(command, 'get_handlers', lambda x: [])("on_reaction"):
            await handler(user, reaction, receiver)
