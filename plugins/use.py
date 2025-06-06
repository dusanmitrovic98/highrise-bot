from highrise import AnchorPosition
from src.commands.command_base import CommandBase
import json
import os

CONFIG_PATH = "config/config.json"

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user, args, message):
        if len(args) < 1:
            await self.bot.highrise.send_whisper(user.id, "Usage: !use <entity_id|name>")
            return
        key = args[0]
        # Try to resolve key as entity name from config
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            entities = config.get("entities", {})
            entity_id = entities.get(key, key)  # Use name if exists, else raw id
        except Exception:
            entity_id = key
        try:
            await self.bot.highrise.walk_to(AnchorPosition(entity_id=entity_id, anchor_ix=0))
        except Exception as e:
            await self.bot.highrise.send_whisper(user.id, f"Failed to use entity: {e}")
