from src.commands.command_base import CommandBase
from src.utility.get_user_by_username import get_user_by_username
import json
import os

WARDROBE_PATH = "config/wardrobe.json"

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user, args, message):
        # Usage: !outfit copy <@username> <name>
        if len(args) == 3 and args[0].lower() == "copy":
            target = args[1]
            name = args[2]
            if target.startswith("@"):
                username = target[1:]
            else:
                username = target
            target_user = await get_user_by_username(self.bot, username)
            if not target_user:
                await self.bot.highrise.send_whisper(user.id, f"User {username} not found in the room.")
                return
            # Get the outfit of the target user
            try:
                resp = await self.bot.highrise.get_user_outfit(target_user.id)
                outfit = resp.outfit if hasattr(resp, "outfit") else getattr(resp, "items", None)
            except Exception:
                outfit = None
            if not outfit:
                await self.bot.highrise.send_whisper(user.id, f"Could not get outfit for {username}.")
                return
            # Save to wardrobe
            wardrobe = self._load_wardrobe()
            wardrobe[name] = outfit
            self._save_wardrobe(wardrobe)
            await self.bot.highrise.send_whisper(user.id, f"Copied {username}'s outfit as '{name}'.")
        else:
            await self.bot.highrise.send_whisper(user.id, "Usage: !outfit copy <@username> <name>")

    def _load_wardrobe(self):
        if not os.path.exists(WARDROBE_PATH):
            return {}
        try:
            with open(WARDROBE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_wardrobe(self, wardrobe):
        os.makedirs(os.path.dirname(WARDROBE_PATH), exist_ok=True)
        with open(WARDROBE_PATH, "w", encoding="utf-8") as f:
            json.dump(wardrobe, f, ensure_ascii=False, indent=2)
