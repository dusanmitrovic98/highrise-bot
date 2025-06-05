from config.config import get_section, set_section
from src.commands.command_base import CommandBase

class Command(CommandBase):
    """
    Command to save or remove portal locations (room name to room ID mappings).
    Usage:
      !portals save <name> <room_id>
      !portals remove <name>
    """
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user, args, message):
        print(f"Executing portals command with args: {args}")
        portals = get_section("portals") or {}
        if not args:
            if not portals:
                await self.bot.highrise.send_whisper(user.id, "No portals saved.")
                return
            msg = "Saved portals:\n" + "\n".join(f"{name}: {room_id}" for name, room_id in portals.items())
            await self.bot.highrise.send_whisper(user.id, msg)
            return
        if args[0] not in ("save", "remove"):
            await self.bot.highrise.send_whisper(user.id, "Usage: !portals save <name> <room_id> | !portals remove <name>")
            return
        action = args[0]
        if action == "save":
            if len(args) < 3:
                await self.bot.highrise.send_whisper(user.id, "Usage: !portals save <name> <room_id>")
                return
            name, room_id = args[1], args[2]
            portals[name] = room_id
            set_section("portals", portals)
            await self.bot.highrise.send_whisper(user.id, f"Portal '{name}' saved with room ID '{room_id}'.")
        elif action == "remove":
            if len(args) < 2:
                await self.bot.highrise.send_whisper(user.id, "Usage: !portals remove <name>")
                return
            name = args[1]
            if name in portals:
                del portals[name]
                set_section("portals", portals)
                await self.bot.highrise.send_whisper(user.id, f"Portal '{name}' removed.")
            else:
                await self.bot.highrise.send_whisper(user.id, f"Portal '{name}' not found.")
