import re
from highrise import User
from config.config import config
from src.utility.utility import load_permissions, save_permissions
from src.commands.command_base import CommandBase

INVALID_COMMAND_MESSAGE = "Invalid command format. Use /grant_permission @username permission OR /grant_role @username role"
USER_NOT_FOUND_MESSAGE = "User {username} not found."
PERMISSION_GRANTED_MESSAGE = "Permission {permission} granted to {username}."
PERMISSION_REVOKED_MESSAGE = "Permission {permission} revoked from {username}."
ROLE_GRANTED_MESSAGE = "Role {role} granted to {username}."
ROLE_REVOKED_MESSAGE = "Role {role} revoked from {username}."
PERMISSION_PATTERN = re.compile(rf"{config.prefix}grant_permission @([\w-]+) (\w+)")
ROLE_PATTERN = re.compile(rf"{config.prefix}grant_role @([\w-]+) (\w+)")
REVOKE_PERMISSION_PATTERN = re.compile(rf"{config.prefix}revoke_permission @([\w-]+) (\w+)")
REVOKE_ROLE_PATTERN = re.compile(rf"{config.prefix}revoke_role @([\w-]+) (\w+)")

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        # Permission is now handled in the handler, no need to check here
        # Grant permission
        match = PERMISSION_PATTERN.match(message.strip())
        if match:
            username, permission = match.groups()
            await self.grant_permission(username, permission, user)
            return
        # Grant role
        match = ROLE_PATTERN.match(message.strip())
        if match:
            username, role = match.groups()
            await self.grant_role(username, role, user)
            return
        # Revoke permission
        match = REVOKE_PERMISSION_PATTERN.match(message.strip())
        if match:
            username, permission = match.groups()
            await self.revoke_permission(username, permission, user)
            return
        # Revoke role
        match = REVOKE_ROLE_PATTERN.match(message.strip())
        if match:
            username, role = match.groups()
            await self.revoke_role(username, role, user)
            return
        await self.bot.highrise.send_whisper(user.id, INVALID_COMMAND_MESSAGE)

    async def grant_permission(self, username, permission, sender):
        data = load_permissions()
        user_id = self.get_user_id_by_username(data, username)
        if not user_id:
            await self.bot.highrise.send_whisper(sender.id, USER_NOT_FOUND_MESSAGE.format(username=username))
            return
        user_entry = data["users"].setdefault(user_id, {"roles": [], "extra_permissions": []})
        if permission not in user_entry["extra_permissions"]:
            user_entry["extra_permissions"].append(permission)
            save_permissions(data)
        await self.bot.highrise.send_whisper(sender.id, PERMISSION_GRANTED_MESSAGE.format(permission=permission, username=username))

    async def revoke_permission(self, username, permission, sender):
        data = load_permissions()
        user_id = self.get_user_id_by_username(data, username)
        if not user_id:
            await self.bot.highrise.send_whisper(sender.id, USER_NOT_FOUND_MESSAGE.format(username=username))
            return
        user_entry = data["users"].setdefault(user_id, {"roles": [], "extra_permissions": []})
        if permission in user_entry["extra_permissions"]:
            user_entry["extra_permissions"].remove(permission)
            save_permissions(data)
        await self.bot.highrise.send_whisper(sender.id, PERMISSION_REVOKED_MESSAGE.format(permission=permission, username=username))

    async def grant_role(self, username, role, sender):
        data = load_permissions()
        user_id = self.get_user_id_by_username(data, username)
        if not user_id:
            await self.bot.highrise.send_whisper(sender.id, USER_NOT_FOUND_MESSAGE.format(username=username))
            return
        user_entry = data["users"].setdefault(user_id, {"roles": [], "extra_permissions": []})
        if role not in user_entry["roles"]:
            user_entry["roles"].append(role)
            save_permissions(data)
        await self.bot.highrise.send_whisper(sender.id, ROLE_GRANTED_MESSAGE.format(role=role, username=username))

    async def revoke_role(self, username, role, sender):
        data = load_permissions()
        user_id = self.get_user_id_by_username(data, username)
        if not user_id:
            await self.bot.highrise.send_whisper(sender.id, USER_NOT_FOUND_MESSAGE.format(username=username))
            return
        user_entry = data["users"].setdefault(user_id, {"roles": [], "extra_permissions": []})
        if role in user_entry["roles"]:
            user_entry["roles"].remove(role)
            save_permissions(data)
        await self.bot.highrise.send_whisper(sender.id, ROLE_REVOKED_MESSAGE.format(role=role, username=username))

    def get_user_id_by_username(self, data, username):
        # Try to find user by username in users dict
        for uid, entry in data["users"].items():
            if entry.get("username", "").lower() == username.lower():
                return uid
        return None
