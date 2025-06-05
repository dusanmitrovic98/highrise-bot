from highrise import User, Position
from config.config import get_section
from src.commands.command_base import CommandBase

class Command(CommandBase):
    """
    Command to move the bot to a named location from config.json.
    Usage: !move <location>
    """
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        if not args:
            await self.bot.highrise.send_whisper(user.id, f"Usage: !move <location>")
            return
        location_name = args[0].lower()
        locations_dict = get_section('locations')
        loc = locations_dict.get(location_name)
        print(loc)
        if not loc or not all(k in loc for k in ("x", "y", "z")):
            await self.bot.highrise.send_whisper(user.id, f"{location_name} is not a valid location.")
            return
        facing = loc.get("facing", "FrontRight")
        dest = Position(loc["x"], loc["y"], loc["z"], facing)
        await self.bot.highrise.walk_to(dest)
        await self.bot.highrise.chat(f"Moving to {location_name}!")
