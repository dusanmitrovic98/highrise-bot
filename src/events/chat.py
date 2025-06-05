import logging

from config.config import config, loggers
from highrise.models import User

from .dispatch_util import dispatch_event


async def on_chat(bot, user: User, message: str) -> None:
    try:
        if loggers.messages:
            logging.info(f"(chat) {user.username}: {message}")
        # Run command handler if prefix matches
        if message.lstrip().startswith(config.prefix):
            await bot.command_handler.handle_command(user, message)
        # Dispatch to all plugin/command on_chat handlers
        await dispatch_event(bot, "on_chat", user, message)
    except Exception as e:
        logging.error(f"Error in on_chat: {e}", exc_info=True)
