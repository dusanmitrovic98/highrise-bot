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
        def normalize_facing(facing_str, default):
            facing_map = {
                'frontright': 'FrontRight',
                'frontleft': 'FrontLeft',
                'backright': 'BackRight',
                'backleft': 'BackLeft',
                'front': 'FrontRight',
                'back': 'BackRight',
                'left': 'FrontLeft',
                'right': 'FrontRight',
            }
            key = facing_str.replace(' ', '').lower()
            return facing_map.get(key, default)

        if len(pos_args) == 3 or len(pos_args) == 4:
            try:
                x, y, z = float(pos_args[0]), float(pos_args[1]), float(pos_args[2])
                if len(pos_args) == 4:
                    facing_raw = pos_args[3]
                    # Get user's current facing if not valid
                    user_pos = None
                    for content in response.content:
                        if content[0].id == target_user_id:
                            if len(content) > 1:
                                user_pos = content[1]
                            break
                    default_facing = getattr(user_pos, 'facing', 'FrontRight') if user_pos else 'FrontRight'
                    facing = normalize_facing(facing_raw, default_facing)
                else:
                    user_pos = None
                    for content in response.content:
                        if content[0].id == target_user_id:
                            if len(content) > 1:
                                user_pos = content[1]
                            break
                    facing = getattr(user_pos, 'facing', 'FrontRight') if user_pos else 'FrontRight'
                dest = Position(x, y, z, facing)
            except ValueError:
                await self.bot.highrise.send_whisper(user.id, "Invalid coordinates")
                return
        else:
            position_name = " ".join(pos_args).lower()
            locations_dict = get_section('locations')
            loc = locations_dict.get(position_name)
            if loc and all(k in loc for k in ("x", "y", "z")):
                facing = loc.get("facing", "FrontRight")
                facing = normalize_facing(facing, "FrontRight")
                dest = Position(loc["x"], loc["y"], loc["z"], facing)
                await self.bot.highrise.chat(f"Teleporting to {dest}!")
            else:
                await self.bot.highrise.send_whisper(user.id, f"{position_name} is not a valid position in this room.")
                return
        if not target_user_id:
            await self.bot.highrise.send_whisper(user.id, "User not found")
            return
        await self.bot.highrise.teleport(target_user_id, dest)
