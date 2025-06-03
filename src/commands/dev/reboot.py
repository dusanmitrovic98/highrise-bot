import os
from highrise import User
from src.commands.command_base import CommandBase
from src.handlers.handleCommands import get_user_permissions

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        user_permissions = get_user_permissions(user)
        # Allow if user has '*' (owner), 'admin', or 'owner' in permissions
        if not ("*" in user_permissions or "admin" in user_permissions or "owner" in user_permissions):
            await self.bot.highrise.send_whisper(user.id, "You do not have permission to reset the bot.")
            return
        await self.bot.highrise.chat("Bot is restarting by admin command.")
        os._exit(0)
