from highrise import User, Position
from config.config import messages, permissions
from src.commands.command_base import CommandBase

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
        """
        Execute the come command.
        
        :param user: The user who issued the command.
        :param args: The arguments passed with the command.
        :param message: The message containing the command.
        """
        if not self.is_owner(user.id):
            await self.bot.highrise.send_whisper(user.id, OWNER_ONLY_MESSAGE)
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
        return user_id in permissions.owners

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
