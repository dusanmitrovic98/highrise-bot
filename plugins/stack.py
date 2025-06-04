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
            await self.bot.highrise.send_whisper(user.id, "Usage: !stack @user1 @user2 ... [spacing]")
            return
        # Check for optional spacing at the end
        try:
            spacing = float(args[-1])
            usernames = [a[1:] for a in args[:-1] if a.startswith("@")]
        except ValueError:
            spacing = 3.0
            usernames = [a[1:] for a in args if a.startswith("@")]
        # If only one user is mentioned, stack on top of the caller
        if len(usernames) == 1:
            usernames.insert(0, user.username)
        if not usernames or len(usernames) < 2:
            await self.bot.highrise.send_whisper(user.id, "No valid @usernames provided or not enough users to stack.")
            return
        positions = []
        users = []
        for uname in usernames:
            u, pos = await get_user_and_pos(self.bot, uname)
            if not u:
                await self.bot.highrise.send_whisper(user.id, f"User {uname} not found.")
                return
            users.append(u)
            positions.append(pos)
        # Always stack on top of the first user's position
        base = positions[0]
        for i, u in enumerate(users):
            if i == 0:
                continue  # Do not teleport the base user
            dest = Position(base.x, base.y + i * spacing, base.z, facing=getattr(base, 'facing', 'FrontRight'))
            await self.bot.highrise.teleport(u.id, dest)
        await self.bot.highrise.send_whisper(user.id, f"Stacked {' '.join([u.username for u in users])} with spacing {spacing}.")
