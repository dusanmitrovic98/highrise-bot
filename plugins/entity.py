from highrise import AnchorPosition, User
from src.commands.command_base import CommandBase
import json
import os

CONFIG_PATH = "config/config.json"

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args, message):
        if len(args) < 2 or args[0] != "save":
            await self.bot.highrise.send_whisper(user.id, "Usage: !entity save <name>")
            return
        name = args[1]
        # Get user's current position
        users = await self.bot.highrise.get_room_users()
        anchor_id = None
        for u, pos in users.content:
            if u.id == user.id and hasattr(pos, 'entity_id'):
                anchor_id = pos.entity_id
                break
        if not anchor_id:
            await self.bot.highrise.send_whisper(user.id, "You are not anchored to any entity.")
            return
        # Load config
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        # Ensure 'entities' exists
        if "entities" not in config or not isinstance(config["entities"], dict):
            config["entities"] = {}
        config["entities"][name] = anchor_id
        # Save config
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        await self.bot.highrise.send_whisper(user.id, f"Saved entity '{name}' with id {anchor_id}.")
