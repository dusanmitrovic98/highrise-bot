from highrise import User
from config.config import get_section, set_section
from src.commands.command_base import CommandBase

class Command(CommandBase):
    """
    Command to display, save, and remove locations from config.json.
    Usage:
      !locations                - List all saved locations
      !locations save <name>    - Save current user's position as <name>
      !locations remove <name>  - Remove location <name>
    """
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        if not args:
            # List all locations
            locations = get_section('locations')
            location_names = list(locations.keys())
            if location_names:
                locations_str = ", ".join(location_names)
                await self.bot.highrise.send_whisper(user.id, f"Saved locations: {locations_str}")
            else:
                await self.bot.highrise.send_whisper(user.id, "No locations saved.")
            return
        subcmd = args[0].lower()
        if subcmd == "save" and len(args) == 2:
            loc_name = args[1].lower()
            # Get user's current position
            response = await self.bot.highrise.get_room_users()
            user_position = None
            for content in response.content:
                if content[0].id == user.id:
                    if len(content) > 1:
                        user_position = content[1]
                    break
            if not user_position:
                await self.bot.highrise.send_whisper(user.id, "Could not determine your current position.")
                return
            # Save to config.json as a flat key
            locations = get_section('locations')
            locations[loc_name] = {
                "x": user_position.x,
                "y": user_position.y,
                "z": user_position.z,
                "facing": getattr(user_position, 'facing', 'Front')
            }
            set_section('locations', locations)
            await self.bot.highrise.send_whisper(user.id, f"Location '{loc_name}' saved.")
            return
        if subcmd == "remove" and len(args) == 2:
            loc_name = args[1].lower()
            locations = get_section('locations')
            if loc_name in locations:
                del locations[loc_name]
                set_section('locations', locations)
                await self.bot.highrise.send_whisper(user.id, f"Location '{loc_name}' removed.")
            else:
                await self.bot.highrise.send_whisper(user.id, f"Location '{loc_name}' not found.")
            return
        await self.bot.highrise.send_whisper(user.id, "Usage: !locations [save <name>|remove <name>]")
