import re
from highrise import User
from config.config import config, permissions
from src.utility.utility import (
    get_user, get_user_id, load_permissions, save_permissions,
    user_exists, username_exists
)

COMMAND_NAME = "give_permission"
COMMAND_DESCRIPTION = "Give a permission to a user"
COMMAND_ALIASES = ['speak', 'talk']
COMMAND_COOLDOWN = 10
INVALID_COMMAND_MESSAGE = "Invalid command format. Use /give_permission @username permission"
USER_NOT_FOUND_MESSAGE = "User {username} not found."
PERMISSION_GRANTED_MESSAGE = "Permission {permission} granted to {username}."
PERMISSION_PATTERN = re.compile(rf"{config.prefix}give_permission @(\w+) (\w+)")

class Command:
    """
    Command to give a permission to a user.
    """
    def __init__(self, bot):
        """
        Initialize the give_permission command with the bot instance.
        """
        self.bot = bot
        self.name = COMMAND_NAME
        self.description = COMMAND_DESCRIPTION
        self.aliases = COMMAND_ALIASES
        self.cooldown = COMMAND_COOLDOWN

    async def execute(self, user: User, args: list, message: str):
        """
        Execute the give_permission command.
        
        :param user: The user who issued the command.
        :param args: The arguments passed with the command.
        :param message: The message containing the command.
        """
        match = PERMISSION_PATTERN.match(message.strip())
        if not match:
            await self.bot.highrise.chat(INVALID_COMMAND_MESSAGE)
            return

        username = match.group(1)
        permission = match.group(2)

        users = load_permissions()["permissions"]

        if not username_exists(users, username):
            await self.bot.highrise.chat(USER_NOT_FOUND_MESSAGE.format(username=username))
            return

        target_user = User(id=get_user_id(users, username), username=username)
        set_permission_to_user(target_user, permission)
        
        await self.bot.highrise.chat(PERMISSION_GRANTED_MESSAGE.format(permission=permission, username=username))

def set_permission_to_user(user: User, permission: str):
    """
    Set a permission to a user.
    
    :param user: The user to set the permission for.
    :param permission: The permission to set.
    """
    data = load_permissions()
    if user_exists(data['permissions'], user.id):
        existing_user = get_user(data['permissions'], user.id)
        if permission not in existing_user['permissions']:
            existing_user['permissions'].append(permission)
    else:
        new_user = {
            'user_id': user.id,
            'username': user.username,
            'permissions': permissions.default
        }
        if permission not in new_user['permissions']:
            new_user['permissions'].append(permission)
        data['permissions'].append(new_user)

    save_permissions(data)
