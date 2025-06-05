from highrise.models import User
from config.config import loggers
import logging


async def on_join(bot, user: User) -> None:
    if loggers.joins:
        logging.info(f"User joined: {user.username}:{user.id}")
    await bot.highrise.chat(f"{user.username} Joined the room!")

    # Dispatch to all plugin/command on_join handlers
    for command in getattr(bot, 'commands', []):
        for handler in getattr(command, 'get_handlers', lambda x: [])("on_join"):
            await handler(user)
