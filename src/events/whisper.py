from config.config import config
from highrise.models import User

from .dispatch_util import dispatch_event


async def on_whisper(bot, user: User, message: str) -> None:
    if message.lstrip().startswith(config.prefix):
        await bot.command_handler.handle_command(user, message)
    await dispatch_event(bot, "on_whisper", user, message)
