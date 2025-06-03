import logging
from highrise import User
from src.commands.command_base import CommandBase

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "reload"
        self.description = "Reload all commands and plugins (admin/owner only)."
        self.cooldown = 0
        self.permissions = ["admin", "owner"]
        self.aliases = []

    async def execute(self, user: User, args: list, message: str):
        from src.handlers.handleCommands import get_user_permissions
        user_permissions = get_user_permissions(user)
        if not ("admin" in user_permissions or "owner" in user_permissions):
            await self.bot.highrise.send_whisper(user.id, "You do not have permission to reload commands.")
            return
        try:
            self.bot.command_handler.load_commands()
            await self.bot.highrise.send_whisper(user.id, "Commands and plugins reloaded successfully.")
            logging.info(f"{user.username} reloaded all commands and plugins.")
        except Exception as e:
            await self.bot.highrise.send_whisper(user.id, f"Reload failed: {e}")
            logging.error(f"Reload failed: {e}")
