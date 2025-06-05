import json
from highrise.models import User
from config.config import loggers, config
import logging

async def on_chat(bot, user: User, message: str) -> None:
    try:
        if loggers.messages:
            logging.info(f"(chat) {user.username}: {message}")
        if message.lstrip().startswith(config.prefix):
            await bot.command_handler.handle_command(user, message)
    except Exception as e:
        logging.error(f"Error in on_chat: {e}", exc_info=True)
