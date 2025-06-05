import logging

from config.config import config, loggers
from highrise.models import User

from .dispatch_util import dispatch_event


async def on_whisper(bot, user: User, message: str) -> None:
    if loggers.whispers:
        logging.info(f"(whisper) {user.username}: {message}")
    if message.lstrip().startswith(config.prefix):
        await bot.command_handler.handle_command(user, message)

    # Dispatch to all plugin/command on_whisper handlers
    await dispatch_event(bot, "on_whisper", user, message)
