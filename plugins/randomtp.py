import random
from highrise import User, Position
from config.config import messages
from src.commands.command_base import CommandBase

async def get_user_and_pos(bot, username):
    response = await bot.highrise.get_room_users()
    for u, pos in response.content:
        if u.username.lower() == username.lower():
            return u, pos
    return None, None

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        # Optionally allow @username
        target = user
        if args and args[0].startswith("@"):
            target, _ = await get_user_and_pos(self.bot, args[0][1:])
            if not target:
                await self.bot.highrise.send_whisper(user.id, f"User {args[0][1:]} not found.")
                return
        _, pos = await get_user_and_pos(self.bot, target.username)
        # Room bounds (customize as needed)
        min_x, max_x = 0, 10
        min_y, max_y = 0, 2
        min_z, max_z = 0, 10
        new_x = random.uniform(min_x, max_x)
        new_y = random.uniform(min_y, max_y)
        new_z = random.uniform(min_z, max_z)
        dest = Position(new_x, new_y, new_z, facing=getattr(pos, 'facing', 'FrontRight'))
        await self.bot.highrise.teleport(target.id, dest)
        await self.bot.highrise.send_whisper(user.id, f"Randomly teleported {target.username}!")
