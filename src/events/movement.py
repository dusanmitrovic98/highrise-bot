from highrise.models import User, Position, AnchorPosition
from config.config import loggers, config
import logging


async def on_move(bot, user: User, destination: Position | AnchorPosition) -> None:
    if loggers.userMovement:
        logging.info(f"{user.username} moved to {destination}")
    # Follow logic: if the bot is set to follow this user, move the bot to the same destination
    if hasattr(config, 'follow_user_id') and getattr(config, 'follow_user_id', None) == user.id:
        await bot.highrise.walk_to(destination)
