import asyncio
import random
from highrise.models import SessionMetadata, Position
from config.config import config, loggers
from src.utility.ai import ask_bot

DIRECTIONS = [
    {'x': 4, 'y': 0.6000, 'z': 0, 'facing': 'FrontRight'},
    {'x': 4, 'y': 0.6000, 'z': 5, 'facing': 'FrontRight'},
    {'x': 0, 'y': 0.6000, 'z': 5, 'facing': 'FrontLeft'},
    {'x': 2, 'y': 0.6000, 'z': 8, 'facing': 'FrontRight'}
]
SLEEP_INTERVAL = (2, 3)
MOVE_MESSAGE = "You just performed a move action from one position to another. Do something unexpected, interesting. Either say it in a sarcastic funny way or in role-play manner"

async def on_start(bot, session_metadata: SessionMetadata) -> None:
    """
    Initialize the bot at the start of the session.
    
    :param bot: The bot instance.
    :param session_metadata: Metadata about the current session.
    """
    if loggers.SessionMetadata:
        rate_limits = session_metadata.rate_limits
        formatted_rate_limits = ', '.join(str(value) for value in rate_limits.values())
        print(f"Bot ID: {session_metadata.user_id}\nRate Limits: {formatted_rate_limits}\nConnection ID: {session_metadata.connection_id}\nSDK Version: {session_metadata.sdk_version}")

    coords = config.coordinates
    await bot.highrise.walk_to(Position(coords['x'], coords['y'], coords['z'], coords['facing']))
    await bot.highrise.chat(f"\n(RECONNECTED) {config.botName} is now ready.")
    await ask_bot(bot, None, "You were in your thoughts, on your phone or some other excuse. You look at people and apologize. Find some silly fun excuse!")
    await move_randomly(bot)

async def move(bot):
    """
    Move the bot to a random position and perform an action.
    
    :param bot: The bot instance.
    """
    choice = random.choice(DIRECTIONS)
    await ask_bot(bot, None, MOVE_MESSAGE)
    await bot.highrise.walk_to(Position(choice['x'], choice['y'], choice['z'], choice['facing']))

async def move_randomly(bot):
    """
    Move the bot to random positions at random intervals.
    
    :param bot: The bot instance.
    """
    while True:
        await asyncio.sleep(random.uniform(*SLEEP_INTERVAL))
        if config.allowed_to_roam:
            await move(bot)
