from highrise import User, Position
from config.config import config, messages, get_section
from src.commands.command_base import CommandBase


class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        prefix = config.prefix
        response = await self.bot.highrise.get_room_users()
        users = [content[0]
                 for content in response.content]  # Extract the User objects
        usernames = [user.username.lower()
                     for user in users]  # Extract the usernames
        if len(args) < 1:
            await self.bot.highrise.send_whisper(user.id, f"{messages.invalidUsage.format(prefix=prefix, commandName='teleport', args='[@username] <position>')} or {prefix}teleport [@username] x y z")
            return
        # Determine if first arg is a user
        if args[0][0] == "@":
            username_arg = args[0][1:].lower()
            if username_arg not in usernames:
                await self.bot.highrise.send_whisper(user.id, f"{messages.invalidPlayer.format(user=args[0][1:])}")
                return
            target_user_id = next((u.id for u in users if u.username.lower() == username_arg), None)
            pos_args = args[1:]
        else:
            target_user_id = user.id
            pos_args = args

        if len(pos_args) == 3:
            try:
                x, y, z = float(pos_args[0]), float(pos_args[1]), float(pos_args[2])
                dest = Position(x, y, z)
            except ValueError:
                await self.bot.highrise.send_whisper(user.id, "Invalid coordinates")
                return
        else:
            position_name = " ".join(pos_args).lower()
            locations_dict = get_section('locations')
            loc = locations_dict.get(position_name)
            if loc and all(k in loc for k in ("x", "y", "z")):
                dest = Position(loc["x"], loc["y"], loc["z"])
            else:
                await self.bot.highrise.send_whisper(user.id, f"{position_name} is not a valid position in this room.")
                return
        if not target_user_id:
            await self.bot.highrise.send_whisper(user.id, "User not found")
            return
        await self.bot.highrise.teleport(target_user_id, dest)
