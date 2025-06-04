import json
from highrise import User, Position
from config.config import config, messages
from src.commands.command_base import CommandBase


class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)
        with open("config/json/locations.json") as f:
            self.room_positions = json.load(f)

    async def execute(self, user: User, args: list, message: str):
        prefix = config.prefix
        response = await self.bot.highrise.get_room_users()
        users = [content[0]
                 for content in response.content]  # Extract the User objects
        usernames = [user.username.lower()
                     for user in users]  # Extract the usernames
        if len(args) < 2:
            await self.bot.highrise.send_whisper(user.id, f"{messages.invalidUsage.format(prefix=prefix, commandName='teleport', args='@username <position>')} or {prefix}teleport @username x y z")
            return
        elif args[0][0] != "@":
            await self.bot.highrise.send_whisper(user.id, f"{messages.invalidUserFormat}")
            return
        elif args[0][1:].lower() not in usernames:
            await self.bot.highrise.send_whisper(user.id, f"{messages.invalidPlayer.format(user=args[0][1:])}")
            return
        elif len(args) == 4:
            try:
                x, y, z = float(args[1]), float(args[2]), float(args[3])
                dest = Position(x, y, z)
            except ValueError:
                await self.bot.highrise.send_whisper(user.id, "Invalid coordinates")
                return
        else:
            position_name = " ".join(args[1:])
            found = False
            for group, locations in self.room_positions.items():
                if position_name in locations:
                    dest = Position(*locations[position_name])
                    found = True
                    break
            if not found:
                await self.bot.highrise.send_whisper(user.id, f"{position_name} is not a valid position in this room.")
                return

        user_id = next(
            (u.id for u in users if u.username.lower() == args[0][1:].lower()), None)
        if not user_id:
            await self.bot.highrise.send_whisper(user.id, f"User {args[0][1:]} not found")
            await self.bot.highrise.send_whisper(user.id, f"{messages.invalidUser.format(user=args[0][1:])}")
            return
        await self.bot.highrise.teleport(user_id, dest)
