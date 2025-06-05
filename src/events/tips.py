from highrise.models import CurrencyItem, Item, User
from config.config import loggers
import logging

from src.utility.ai import ask_bot
from .dispatch_util import dispatch_event


async def on_tip(bot, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
    if loggers.tips:
        logging.info(f"{sender.username} tipped {receiver.username} {tip.amount} {tip.type}!")
    await bot.highrise.chat(f"{sender.username} tipped {receiver.username} {tip.amount} {tip.type}!")
    await ask_bot(bot, sender, f"{sender.username} tipped {receiver.username} {tip.amount} {tip.type}! This person just tipped another person this amount of gold that are your thoughts?")
    # Dispatch to all plugin/command on_tip handlers
    await dispatch_event(bot, "on_tip", sender, receiver, tip)
