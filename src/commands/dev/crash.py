import os
from highrise import User
from src.commands.command_base import CommandBase

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "crash"
        self.description = "Force the bot to crash for testing restart logic."
        self.cooldown = 0
        self.permissions = ["admin"]
        self.aliases = []

    async def execute(self, user: User, args: list, message: str):
        from src.handlers.handleCommands import get_user_permissions
        user_permissions = get_user_permissions(user)
        # Allow if user has '*' (owner), 'admin', or 'owner' in permissions
        if not ("*" in user_permissions or "admin" in user_permissions or "owner" in user_permissions):
            await self.bot.highrise.send_whisper(user.id, "You do not have permission to crash the bot.")
            return
        await self.bot.highrise.chat("Bot is crashing down by admin command.")
        os._exit(1)
