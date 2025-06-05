from highrise.models import User
from config.config import loggers, config
import logging


async def on_whisper(bot, user: User, message: str) -> None:
    if loggers.whispers:
        logging.info(f"(whisper) {user.username}: {message}")
    if message.lstrip().startswith(config.prefix):
        await bot.command_handler.handle_command(user, message)

    # Dispatch to all plugin/command on_whisper handlers
    for command in getattr(bot, 'commands', []):
        for handler in getattr(command, 'get_handlers', lambda x: [])("on_whisper"):
            await handler(user, message)
