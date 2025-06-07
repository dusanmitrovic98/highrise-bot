from src.commands.command_base import CommandBase
import json
import os
from attrs import asdict

WARDROBE_PATH = "config/wardrobe.json"

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user, args, message):
        # Accept both '!wardrobe' and '!wardrobe open' for listing
        if not args or (len(args) == 1 and args[0].lower() == "open"):
            outfits = self._load_wardrobe()
            if outfits:
                outfits_list = "\n".join(outfits.keys())
                await self.bot.highrise.send_whisper(user.id, f"Saved outfits:\n{outfits_list}")
            else:
                await self.bot.highrise.send_whisper(user.id, "No outfits saved.")
            return
        cmd = args[0].lower()
        if cmd == "save" and len(args) > 1:
            name = args[1]
            outfit = await self._get_current_outfit()
            if outfit is None:
                await self.bot.highrise.send_whisper(user.id, "Failed to get current outfit.")
                return
            # Convert all items to dicts for JSON serialization
            if isinstance(outfit, dict):
                serializable_outfit = {k: asdict(v) if hasattr(v, '__attrs_attrs__') else v for k, v in outfit.items()}
            elif isinstance(outfit, list):
                serializable_outfit = [asdict(i) if hasattr(i, '__attrs_attrs__') else i for i in outfit]
            else:
                serializable_outfit = asdict(outfit) if hasattr(outfit, '__attrs_attrs__') else outfit
            wardrobe = self._load_wardrobe()
            wardrobe[name] = serializable_outfit
            self._save_wardrobe(wardrobe)
            await self.bot.highrise.send_whisper(user.id, f"Outfit '{name}' saved.")
        elif cmd == "remove" and len(args) > 1:
            name = args[1]
            wardrobe = self._load_wardrobe()
            if name in wardrobe:
                del wardrobe[name]
                self._save_wardrobe(wardrobe)
                await self.bot.highrise.send_whisper(user.id, f"Outfit '{name}' removed.")
            else:
                await self.bot.highrise.send_whisper(user.id, f"Outfit '{name}' not found.")
        elif cmd == "wear" and len(args) > 1:
            name = args[1]
            wardrobe = self._load_wardrobe()
            if name in wardrobe:
                outfit = wardrobe[name]
                # Ensure outfit is a list of Item objects (not dicts)
                from highrise.models import Item
                if isinstance(outfit, dict):
                    outfit = list(outfit.values())
                if isinstance(outfit, list):
                    try:
                        item_objs = [Item(**item) if isinstance(item, dict) else item for item in outfit]
                    except Exception as e:
                        await self.bot.highrise.send_whisper(user.id, f"Failed to parse outfit '{name}': {e}")
                        return
                else:
                    await self.bot.highrise.send_whisper(user.id, f"Outfit '{name}' is not a valid list.")
                    return
                try:
                    await self.bot.highrise.set_outfit(item_objs)
                    await self.bot.highrise.send_whisper(user.id, f"Wearing outfit '{name}'.")
                except Exception as e:
                    await self.bot.highrise.send_whisper(user.id, f"Failed to wear outfit '{name}': {e}")
            else:
                await self.bot.highrise.send_whisper(user.id, f"Outfit '{name}' not found.")
        elif cmd == "copy" and len(args) > 1:
            target = args[1]
            if target.startswith("@"): 
                username = target[1:]
            else:
                username = target
            from src.utility.get_user_by_username import get_user_by_username
            target_user = await get_user_by_username(self.bot, username)
            if not target_user:
                await self.bot.highrise.send_whisper(user.id, f"User {username} not found in the room.")
                return
            try:
                resp = await self.bot.highrise.get_user_outfit(target_user.id)
                outfit = resp.outfit if hasattr(resp, "outfit") else getattr(resp, "items", None)
            except Exception:
                outfit = None
            if not outfit:
                await self.bot.highrise.send_whisper(user.id, f"Could not get outfit for {username}.")
                return
            try:
                await self.bot.highrise.set_outfit(outfit)
                await self.bot.highrise.send_whisper(user.id, f"Set my outfit to match {username}.")
            except Exception:
                await self.bot.highrise.send_whisper(user.id, f"Failed to set my outfit to {username}'s outfit.")
        else:
            await self.bot.highrise.send_whisper(user.id, "Usage: !wardrobe [save <name>|remove <name>|wear <name>]")

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

    async def _get_current_outfit(self):
        try:
            resp = await self.bot.highrise.get_user_outfit(self.bot.highrise.my_id)
            if hasattr(resp, "outfit"):
                return resp.outfit
            elif hasattr(resp, "items"):
                return resp.items
            else:
                return None
        except Exception:
            return None
