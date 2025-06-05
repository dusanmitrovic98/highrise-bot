from highrise import User, Position
from config.config import messages
from src.commands.command_base import CommandBase

COMING_MESSAGE = "@{username} I'm coming .."

class Command(CommandBase):
    """
    Command to teleport the bot to a player's position.
    """
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        your_pos = await self.get_user_position(user.id)
        if not your_pos:
            await self.bot.highrise.send_whisper(user.id, messages.invalidPosition)
            return
        await self.bot.highrise.chat(COMING_MESSAGE.format(username=user.username))
        await self.bot.highrise.walk_to(your_pos)

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
