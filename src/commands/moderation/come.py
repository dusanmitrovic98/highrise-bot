from highrise import User, Position
from config.config import messages
from src.commands.command_base import CommandBase
from src.handlers.handleCommands import get_user_permissions

COMMAND_NAME = "come"
COMMAND_DESCRIPTION = "Teleport a player to a specific position"
COMMAND_ALIASES = ['walk']
COMMAND_COOLDOWN = 5
OWNER_ONLY_MESSAGE = "This command is owner only command"
INVALID_POSITION_MESSAGE = "Invalid position."
COMING_MESSAGE = "@{username} I'm coming .."

class Command(CommandBase):
    """
    Command to teleport the bot to a player's position.
    """
    def __init__(self, bot):
        super().__init__(bot)
        self.name = COMMAND_NAME
        self.description = COMMAND_DESCRIPTION
        self.aliases = COMMAND_ALIASES
        self.cooldown = COMMAND_COOLDOWN

    async def execute(self, user: User, args: list, message: str):
        user_permissions = get_user_permissions(user)
        # Accept if user has 'come', 'admin', 'owner', or any role name as permission
        if not ("come" in user_permissions or "admin" in user_permissions or "owner" in user_permissions):
            await self.bot.highrise.send_whisper(user.id, "You do not have permission to use the come command.")
            return
        your_pos = await self.get_user_position(user.id)
        if not your_pos:
            await self.bot.highrise.send_whisper(user.id, messages.invalidPosition)
            return
        await self.bot.highrise.chat(COMING_MESSAGE.format(username=user.username))
        await self.bot.highrise.walk_to(your_pos)

    def is_owner(self, user_id: str) -> bool:
        """
        Check if the user is an owner.
        
        :param user_id: The ID of the user.
        :return: True if the user is an owner, False otherwise.
        """
        # Deprecated: use get_user_permissions instead
        return False

    async def get_user_position(self, user_id: str) -> Position:
        """
        Get the position of the user in the room.
        
        :param user_id: The ID of the user.
        :return: The position of the user if found, None otherwise.
        """
        response = await self.bot.highrise.get_room_users()
        for content in response.content:
            if content[0].id == user_id and isinstance(content[1], Position):
                return content[1]
        return None
