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
        # Parse usernames and optional spacing
        usernames = [arg[1:] for arg in args if arg.startswith("@")]
        spacing = 1
        if len(args) > len(usernames):
            try:
                spacing = float(args[-1])
            except ValueError:
                pass
        # If no usernames, teleport the caller to the bot spawn point
        if not usernames:
            # Try to get bot spawn point from config or fallback to (0,0,0)
            spawn_x, spawn_y, spawn_z, spawn_facing = 0, 0, 0, "FrontRight"
            try:
                from config import config as bot_config
                spawn = bot_config.get("spawn", {})
                spawn_x = spawn.get("x", 0)
                spawn_y = spawn.get("y", 0)
                spawn_z = spawn.get("z", 0)
                spawn_facing = spawn.get("facing", "FrontRight")
            except Exception:
                pass
            dest = Position(spawn_x, spawn_y, spawn_z, facing=spawn_facing)
            await self.bot.highrise.teleport(user.id, dest)
            await self.bot.highrise.send_whisper(user.id, "You have been teleported to the bot spawn point.")
            return
        # If only one user is mentioned, use the caller as the base location
        if len(usernames) == 1:
            usernames.insert(0, user.username)
        # Get user objects and positions
        user_pos_list = []
        for uname in usernames:
            u, pos = await get_user_and_pos(self.bot, uname)
            if not u or not pos:
                await self.bot.highrise.send_whisper(user.id, f"User {uname} not found.")
                return
            user_pos_list.append((u, pos))
        # Unstack logic: spread users horizontally (x axis) at the same y/z as the first user (base)
        base_pos = user_pos_list[0][1]
        for i, (u, pos) in enumerate(user_pos_list):
            if i == 0:
                continue  # Do not teleport the base user
            new_x = base_pos.x + i * spacing
            new_pos = Position(new_x, base_pos.y, base_pos.z, facing=getattr(pos, 'facing', 'FrontRight'))
            await self.bot.highrise.teleport(u.id, new_pos)
        await self.bot.highrise.send_whisper(user.id, f"Unstacked users: {', '.join([u.username for u, _ in user_pos_list])}.")
