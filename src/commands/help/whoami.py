from src.commands.command_base import CommandBase
from highrise import User

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "whoami"
        self.description = "Show your user ID, username, and permissions."
        self.cooldown = 3
        self.permissions = []
        self.aliases = ["myrole", "myperms", "permissions"]

    async def execute(self, user: User, args: list, message: str):
        from src.handlers.handleCommands import get_user_permissions
        perms = get_user_permissions(user)
        msg = f"User: {user.username} (ID: {user.id})\nPermissions: {', '.join([p for p in perms if p]) or 'None'}"
        await self.bot.highrise.send_whisper(user.id, msg)
