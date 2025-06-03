import logging
from quattro import TaskGroup

async def before_start(bot, tg: TaskGroup) -> None:
    """
    Called before the bot starts. You can use this to set up resources, schedule tasks, or log startup info.
    :param bot: The bot instance.
    :param tg: The TaskGroup for scheduling background tasks.
    """
    logging.info("[BEFORE_START] Bot is about to start. You can set up resources here.")
    # Example: schedule a background task (uncomment if needed)
    # tg.create_task(your_background_task())
