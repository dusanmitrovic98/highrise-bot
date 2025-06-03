from pathlib import Path
from highrise import User
import os

class Command:
    def __init__(self, bot):
        self.bot = bot
        self.name = "shutdown"
        self.description = "Shut down the bot (admin only)."
        self.cooldown = 0
        self.permissions = ["admin"]
        self.aliases = []

    async def execute(self, user: User, args: list, message: str):
        # Only allow owners to shutdown
        from config.config import permissions
        if user.id not in permissions.owners:
            await self.bot.highrise.send_whisper(user.id, "You do not have permission to shut down the bot.")
            return
        shutdown_flag = Path("shutdown.flag")
        shutdown_flag.write_text("Shutdown requested by admin")
        await self.bot.highrise.chat("Bot is shutting down by admin command.")
        os._exit(0)
