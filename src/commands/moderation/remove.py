import re
from highrise import User
from config.config import config
from src.utility.utility import load_permissions, save_permissions
from src.commands.command_base import CommandBase

INVALID_COMMAND_MESSAGE = "Invalid command format. Use !remove role|permission @username name"
USER_NOT_FOUND_MESSAGE = "User {username} not found."
PERMISSION_REVOKED_MESSAGE = "Permission {permission} revoked from {username}."
ROLE_REVOKED_MESSAGE = "Role {role} revoked from {username}."

REMOVE_PATTERN = re.compile(rf"{config.prefix}remove (role|permission) @([\w-]+) (\w+)")

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        match = REMOVE_PATTERN.match(message.strip())
        if match:
            type_, username, name = match.groups()
            if type_ == "role":
                await self.remove_role(username, name, user)
            else:
                await self.remove_permission(username, name, user)
            return
        await self.bot.highrise.send_whisper(user.id, INVALID_COMMAND_MESSAGE)

    async def remove_permission(self, username, permission, sender):
        data = load_permissions()
        user_id = self.get_user_id_by_username(data, username)
        if not user_id:
            await self.bot.highrise.send_whisper(sender.id, USER_NOT_FOUND_MESSAGE.format(username=username))
            return
        user_entry = data["users"].setdefault(user_id, {"roles": ["user"], "extra_permissions": [], "username": username})
        if permission in user_entry["extra_permissions"]:
            user_entry["extra_permissions"].remove(permission)
            save_permissions(data)
            await self.bot.highrise.send_whisper(sender.id, PERMISSION_REVOKED_MESSAGE.format(permission=permission, username=username))
        else:
            await self.bot.highrise.send_whisper(sender.id, f"Permission {permission} not found for {username}.")

    async def remove_role(self, username, role, sender):
        data = load_permissions()
        user_id = self.get_user_id_by_username(data, username)
        if not user_id:
            await self.bot.highrise.send_whisper(sender.id, USER_NOT_FOUND_MESSAGE.format(username=username))
            return
        user_entry = data["users"].setdefault(user_id, {"roles": ["user"], "extra_permissions": [], "username": username})
        if role in user_entry["roles"]:
            user_entry["roles"].remove(role)
            save_permissions(data)
            await self.bot.highrise.send_whisper(sender.id, ROLE_REVOKED_MESSAGE.format(role=role, username=username))
        else:
            await self.bot.highrise.send_whisper(sender.id, f"Role {role} not found for {username}.")

    def get_user_id_by_username(self, data, username):
        for uid, entry in data["users"].items():
            if entry.get("username", "").lower() == username.lower():
                return uid
        return None
