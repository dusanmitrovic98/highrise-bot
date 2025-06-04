from highrise import User, Position
from config.config import messages
from src.commands.command_base import CommandBase

async def get_user_and_pos(bot, username):
    response = await bot.highrise.get_room_users()
    for u, pos in response.content:
        if u.username.lower() == username.lower():
            print(f"Found user: {u} at position {pos}")
            return u, pos
    return None, None

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        # If no arguments are provided, show usage instructions
        if len(args) < 1:
            await self.bot.highrise.send_whisper(user.id, "Usage: !swap @user1 [@user2]")
            return
        # The first argument must be a username (starting with @)
        if not args[0].startswith("@"):
            await self.bot.highrise.send_whisper(user.id, "First argument must be @username")
            return
        # Extract the first username (user1)
        name1 = args[0][1:]
        # If a second username is provided, use it; otherwise, use the caller's username
        if len(args) > 1 and args[1].startswith("@"):
            name2 = args[1][1:]
        else:
            name2 = user.username
        # Look up both users and their positions in the room
        user1, pos1 = await get_user_and_pos(self.bot, name1)
        user2, pos2 = await get_user_and_pos(self.bot, name2)
        # If either user is not found, notify the caller
        if not user1 or not user2:
            await self.bot.highrise.send_whisper(user.id, "User(s) not found.")
            return
        # Swap logic:
        # 1. Create new Position objects for each user, using the other's position and facing
        position_user_1 = Position(pos2.x, pos2.y, pos2.z, facing=getattr(pos1, 'facing', 'FrontRight'))
        print(f"{user1.username} will get position: {position_user_1}")
        position_user_2 = Position(pos1.x, pos1.y, pos1.z, facing=getattr(pos2, 'facing', 'FrontRight'))
        print(f"{user2.username} will get position: {position_user_2}")
        # 2. Teleport user1 to user2's position and facing, and user2 to user1's position and facing
        await self.bot.highrise.teleport(user1.id, position_user_1)
        await self.bot.highrise.teleport(user2.id, position_user_2)
        # 3. Notify the caller that the swap is complete
        await self.bot.highrise.send_whisper(user.id, f"Swapped {user1.username} and {user2.username} (including facing direction).")
