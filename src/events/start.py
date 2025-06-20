from config.config import config
from highrise.models import Position, SessionMetadata
from src.utility.ai import ask_bot

from .dispatch_util import dispatch_event


async def on_start(bot, session_metadata: SessionMetadata) -> None:
    """
    Initialize the bot at the start of the session.
    
    :param bot: The bot instance.
    :param session_metadata: Metadata about the current session.
    """
    # if loggers.SessionMetadata:
    #     rate_limits = session_metadata.rate_limits
    #     formatted_rate_limits = ', '.join(str(value) for value in rate_limits.values())
    #     print(f"Bot ID: {session_metadata.user_id}\nRate Limits: {formatted_rate_limits}\nConnection ID: {session_metadata.connection_id}\nSDK Version: {session_metadata.sdk_version}")
    coords = config.locations.spawn
    await bot.highrise.walk_to(Position(coords['x'], coords['y'], coords['z'], coords['facing']))
    await bot.highrise.chat(f"\n(RECONNECTED) {config.bot_name} is now ready.")
    await ask_bot(bot, None, "You were in your thoughts, on your phone or some other excuse. You look at people and apologize. Find some silly fun excuse!")
    await dispatch_event(bot, "on_start", session_metadata)
