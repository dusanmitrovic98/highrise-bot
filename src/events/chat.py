import json
from highrise.models import User
from config.config import loggers, config
import logging

async def on_chat(bot, user: User, message: str) -> None:
    try:
        if loggers.messages:
            logging.info(f"(chat) {user.username}: {message}")
        # Run command handler if prefix matches
        if message.lstrip().startswith(config.prefix):
            await bot.command_handler.handle_command(user, message)
        # Dispatch to all plugin/command on_chat handlers
        print(f"DEBUG: bot.commands = {[getattr(cmd, 'name', cmd) for cmd in getattr(bot, 'commands', [])]}")
        for command in getattr(bot, 'commands', []):
            print(f"DEBUG: Dispatching to command: {getattr(command, 'name', command)}")
            for handler in getattr(command, 'get_handlers', lambda x: [])("on_chat"):
                print(f"DEBUG: Found on_chat handler: {handler}")
                await handler(user, message)
    except Exception as e:
        logging.error(f"Error in on_chat: {e}", exc_info=True)
