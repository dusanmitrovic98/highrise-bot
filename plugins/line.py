import asyncio
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
        if len(args) < 1:
            await self.bot.highrise.send_whisper(user.id, "Usage: !line @user1 [@user2 ...] [spacing]")
            return
        # Parse usernames and optional spacing (no direction)
        usernames = []
        spacing = 1.0
        i = 0
        while i < len(args) and args[i].startswith("@"):
            usernames.append(args[i].lstrip("@"))
            i += 1
        if i < len(args):
            try:
                spacing = float(args[i])
            except ValueError:
                pass
        if not usernames:
            await self.bot.highrise.send_whisper(user.id, "No valid @usernames provided.")
            return
        # If only one mention, include the caller as the first user
        if len(usernames) == 1:
            usernames = [user.username] + usernames
        # Get user objects and positions
        users_pos = []
        for uname in usernames:
            u, pos = await get_user_and_pos(self.bot, uname)
            if not u:
                await self.bot.highrise.send_whisper(user.id, f"User {uname} not found.")
                return
            users_pos.append((u, pos))
        # Use first and last user's position as endpoints
        start = users_pos[0][1]
        end = users_pos[-1][1]
        n = len(users_pos)
        # Calculate center point between start and end
        center_x = (start.x + end.x) / 2
        center_y = (start.y + end.y) / 2
        center_z = (start.z + end.z) / 2
        # Calculate total line length
        total_length = (n - 1) * spacing
        # The first user's offset from center
        first_offset = -total_length / 2
        # Place all users in a line along x axis, centered at center_x
        target_positions = []
        for i in range(n):
            x = center_x + first_offset + i * spacing
            y = center_y
            z = center_z
            if i != 0:
                z -= 0.000000000000001
            target_positions.append(Position(x, y, z))
        # Teleport all users in parallel
        await asyncio.gather(*[
            self.bot.highrise.teleport(users_pos[i][0].id, target_positions[i])
            for i in range(len(users_pos))
        ])
        await self.bot.highrise.send_whisper(user.id, f"Lined up {' '.join([u.username for u, _ in users_pos])} with spacing {spacing}.")
