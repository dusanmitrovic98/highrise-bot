from src.commands.command_base import CommandBase
from highrise import User
import os
import sys

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "reset"
        self.description = "Restart the bot process (admin only)."
        self.cooldown = 0
        self.permissions = ["admin"]
        self.aliases = ["restart"]

    async def execute(self, user: User, args: list, message: str):
        from config.config import permissions
        if user.id not in permissions.owners:
            await self.bot.highrise.send_whisper(user.id, "You do not have permission to reset the bot.")
            return
        await self.bot.highrise.chat("Bot is restarting by admin command.")
        # On Windows, use os.execl to restart the current process
        os.execl(sys.executable, sys.executable, *os.sys.argv)
