import math
from highrise import User, Position
from config.config import messages
from src.commands.command_base import CommandBase

# Helper to get user and position from room
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
        if len(args) < 2:
            await self.bot.highrise.send_whisper(user.id, "Usage: !push @username <distance>")
            return
        if not args[0].startswith("@"):
            await self.bot.highrise.send_whisper(user.id, "First argument must be @username")
            return
        target_name = args[0][1:]
        try:
            distance = float(args[1])
        except ValueError:
            await self.bot.highrise.send_whisper(user.id, "Invalid distance.")
            return
        target, target_pos = await get_user_and_pos(self.bot, target_name)
        if not target:
            await self.bot.highrise.send_whisper(user.id, f"User {target_name} not found.")
            return
        # Get pusher position
        _, user_pos = await get_user_and_pos(self.bot, user.username)
        # Vector from user to target
        dx = target_pos.x - user_pos.x
        dz = target_pos.z - user_pos.z
        mag = math.sqrt(dx*dx + dz*dz)
        if mag == 0:
            await self.bot.highrise.send_whisper(user.id, "Cannot push: same position.")
            return
        dx /= mag
        dz /= mag
        new_x = target_pos.x + dx * distance
        new_z = target_pos.z + dz * distance
        dest = Position(new_x, target_pos.y, new_z, facing=getattr(target_pos, 'facing', 'FrontRight'))
        await self.bot.highrise.teleport(target.id, dest)
        await self.bot.highrise.send_whisper(user.id, f"Pushed {target.username} {distance} units away.")
