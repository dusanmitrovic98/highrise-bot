from highrise import User
from src.commands.command_base import CommandBase
import json

CONFIG_PATH = "config/config.json"

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args, message):
        # Load config
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        entities = config.get("entities", {})
        if not entities:
            await self.bot.highrise.send_whisper(user.id, "No entities saved.")
            return
        lines = [f"{name}: {eid}" for name, eid in entities.items()]
        msg = "Saved entities:\n" + "\n".join(lines)
        await self.bot.highrise.send_whisper(user.id, msg)
