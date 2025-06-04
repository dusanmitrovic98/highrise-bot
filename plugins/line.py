import math
from highrise import User, Position
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
        if len(args) < 2:
            await self.bot.highrise.send_whisper(user.id, "Usage: !line @user1 @user2 ... <direction> [spacing]")
            return
        # Find direction and optional spacing
        try:
            spacing = float(args[-1])
            direction = args[-2].lower()
            usernames = [a[1:] for a in args[:-2] if a.startswith("@")]
        except ValueError:
            spacing = 1.0
            direction = args[-1].lower()
            usernames = [a[1:] for a in args[:-1] if a.startswith("@")]
        if not usernames:
            await self.bot.highrise.send_whisper(user.id, "No valid @usernames provided.")
            return
        users_pos = []
        for uname in usernames:
            u, pos = await get_user_and_pos(self.bot, uname)
            if not u:
                await self.bot.highrise.send_whisper(user.id, f"User {uname} not found.")
                return
            users_pos.append((u, pos))
        # Use first user's position as base
        base = users_pos[0][1]
        # Direction vector
        facing_map = {
            'right': 0,
            'left': 180,
            'forward': 90,
            'back': 270,
            'backward': 270
        }
        angle = facing_map.get(direction, 0)
        rad = math.radians(angle)
        dx = math.cos(rad)
        dz = math.sin(rad)
        for i, (u, pos) in enumerate(users_pos):
            dest = Position(base.x + (i+1) * dx * spacing, base.y, base.z + (i+1) * dz * spacing, facing=getattr(base, 'facing', 'FrontRight'))
            await self.bot.highrise.teleport(u.id, dest)
        await self.bot.highrise.send_whisper(user.id, f"Lined up {' '.join([u.username for u, _ in users_pos])} {direction} with spacing {spacing}.")
