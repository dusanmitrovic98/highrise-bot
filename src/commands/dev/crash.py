import os

from pathlib import Path
from highrise import User

class Command:
    def __init__(self, bot):
        self.bot = bot
        self.name = "crash"
        self.description = "Force the bot to crash for testing restart logic."
        self.cooldown = 0
        self.permissions = ["admin"]
        self.aliases = []

    async def execute(self, user: User, args: list, message: str):
        await self.bot.highrise.chat("Bot is crashing down by admin command.")
        os._exit(1)
