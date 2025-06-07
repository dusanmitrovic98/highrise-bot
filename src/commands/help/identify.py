from src.commands.command_base import CommandBase
from highrise import User

from src.utility.get_user_by_username import get_user_by_username

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        # If @mention is present, try to identify that user
        if args and args[0].startswith('@'):
            username = args[0][1:]
            target_user = await get_user_by_username(self.bot, username)
            if not target_user:
                await self.bot.highrise.send_whisper(user.id, f"User {username} not found in the room.")
                return
        else:
            target_user = user
        # Separate roles and permissions
        from src.utility.utility import load_users
        data = load_users()
        user_entry = data["users"].get(target_user.id, {})
        roles = user_entry.get("roles", [])
        extra_permissions = user_entry.get("extra_permissions", [])
        msg = (
            f"User: {target_user.username} (ID: {target_user.id})\n"
            f"Roles: {', '.join(roles) or 'None'}\n"
            f"Permissions: {', '.join(extra_permissions) or 'None'}"
        )
        await self.bot.highrise.send_whisper(user.id, msg)
