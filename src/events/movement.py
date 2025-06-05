from highrise.models import User, Position, AnchorPosition
from config.config import loggers, config
import logging
import asyncio
from .dispatch_util import dispatch_event


async def on_move(bot, user: User, destination: Position | AnchorPosition) -> None:
    if loggers.userMovement:
        logging.info(f"{user.username} moved to {destination}")

    # Dispatch to all plugin/command on_move handlers
    await dispatch_event(bot, "on_move", user, destination)