from highrise import User
from config.config import config
from src.commands.command_base import CommandBase

class Command(CommandBase):
    """
    Command to set the bot's current position as the spawn point in config.json.
    Usage: !spawn
    """
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        # Get the bot's current position by searching for its own user ID in the room
        response = await self.bot.highrise.get_room_users()
        bot_position = None
        for content in response.content:
            if content[0].id == self.bot.highrise.my_id:
                if len(content) > 1:
                    bot_position = content[1]
                break
        if not bot_position:
            await self.bot.highrise.chat("Could not determine bot's current position.")
            return
        # Update config.json locations.spawn section
        config.locations.spawn.x = bot_position.x
        config.locations.spawn.y = bot_position.y
        config.locations.spawn.z = bot_position.z
        config.locations.spawn.facing = getattr(bot_position, 'facing', 'Front')
        # Save changes to config.json
        from config.config import set_section
        locations = dict(config.locations.__dict__)
        # Remove private attributes if any
        locations = {k: v.__dict__ if hasattr(v, '__dict__') else v for k, v in locations.items()}
        locations['spawn'] = {
            'x': bot_position.x,
            'y': bot_position.y,
            'z': bot_position.z,
            'facing': getattr(bot_position, 'facing', 'Front')
        }
        set_section('locations', locations)
        await self.bot.highrise.chat(f"Spawn position updated to: x={bot_position.x}, y={bot_position.y}, z={bot_position.z}, facing={getattr(bot_position, 'facing', 'Front')}")
