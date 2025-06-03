import os
from highrise import User
from src.commands.command_base import CommandBase
from src.handlers.handleCommands import get_user_permissions

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "reset"
        self.description = "Restart the bot process (admin only)."
        self.cooldown = 0
        self.permissions = ["admin"]
        self.aliases = ["restart", "reboot"]

    async def execute(self, user: User, args: list, message: str):
        user_permissions = get_user_permissions(user)
        if "admin" not in user_permissions and "owner" not in user_permissions:
            await self.bot.highrise.send_whisper(user.id, "You do not have permission to reset the bot.")
            return
        await self.bot.highrise.chat("Bot is restarting by admin command.")
        os._exit(0)
