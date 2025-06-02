from highrise.models import User
from config.config import loggers, config
import logging


async def on_whisper(bot, user: User, message: str) -> None:
    if loggers.whispers:
        logging.info(f"(whisper) {user.username}: {message}")
    if message.lstrip().startswith(config.prefix):
        await bot.command_handler.handle_command(user, message)
