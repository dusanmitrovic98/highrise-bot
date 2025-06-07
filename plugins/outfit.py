from src.commands.command_base import CommandBase
import json
import os

WARDROBE_PATH = "config/wardrobe.json"

class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user, args, message):
        # Usage: !outfit undress [item_name] | !outfit save <item_name> <item_id> | !outfit remove <item_name> | !outfit wear <item_name>|<item_id>
        if len(args) == 2 and args[0].lower() == "undress" and args[1].lower() == "all":
            # Remove all items in outfits.json from the bot's outfit, even if there are duplicates
            items = self._load_items()
            try:
                current = await self._get_current_outfit()
                item_ids = set(v['id'] for v in items.values())
                filtered = [i for i in current if getattr(i, 'id', None) not in item_ids]
                await self.bot.highrise.set_outfit(filtered)
                await self.bot.highrise.send_whisper(user.id, "I have removed all my saved outfit items.")
            except Exception:
                await self.bot.highrise.send_whisper(user.id, "Failed to undress.")
        elif (len(args) == 1 or len(args) == 2) and args[0].lower() == "undress":
            if len(args) == 2:
                item_name = args[1]
                items = self._load_items()
                if item_name in items:
                    from highrise.models import Item
                    try:
                        current = await self._get_current_outfit()
                        # Remove all occurrences of the item id from the current outfit
                        item_id = items[item_name]['id']
                        filtered = [i for i in current if getattr(i, 'id', None) != item_id]
                        await self.bot.highrise.set_outfit(filtered)
                        await self.bot.highrise.send_whisper(user.id, f"Removed item '{item_name}' from my outfit.")
                    except Exception as e:
                        await self.bot.highrise.send_whisper(user.id, f"Failed to undress item '{item_name}': {e}")
                else:
                    await self.bot.highrise.send_whisper(user.id, f"Item '{item_name}' not found in saved items.")
            else:
                await self.bot.highrise.send_whisper(user.id, "Usage: !outfit undress <item_name>|all")
        elif len(args) == 3 and args[0].lower() == "save":
            item_name = args[1]
            item_id = args[2]
            items = self._load_items()
            if item_name in items:
                await self.bot.highrise.send_whisper(user.id, f"Item name '{item_name}' is already saved.")
                return
            items[item_name] = {"id": item_id}
            self._save_items(items)
            await self.bot.highrise.send_whisper(user.id, f"Item '{item_id}' saved as '{item_name}'.")
        elif len(args) == 2 and args[0].lower() == "remove":
            item_name = args[1]
            items = self._load_items()
            if item_name in items:
                del items[item_name]
                self._save_items(items)
                await self.bot.highrise.send_whisper(user.id, f"Item '{item_name}' removed from saved items.")
            else:
                await self.bot.highrise.send_whisper(user.id, f"Item '{item_name}' not found in saved items.")
        elif len(args) == 2 and args[0].lower() == "wear":
            key = args[1]
            items = self._load_items()
            from highrise.models import Item
            # Try by name first, then by id
            if key in items:
                item_id = items[key]['id']
            else:
                item_id = key
            try:
                # Get current outfit
                current = await self._get_current_outfit()
                # Remove any item with the same id
                filtered = [i for i in current if getattr(i, 'id', None) != item_id]
                # Add the new item
                item_obj = Item(type="clothing", amount=1, id=item_id)
                filtered.append(item_obj)
                await self.bot.highrise.set_outfit(filtered)
                await self.bot.highrise.send_whisper(user.id, f"Wearing item '{item_id}'.")
            except Exception as e:
                await self.bot.highrise.send_whisper(user.id, f"Failed to wear item '{item_id}': {e}")
        elif len(args) == 1 and args[0].lower() == "list":
            items = self._load_items()
            if items:
                # Display in blocks of 10 per message
                item_names = list(items.items())
                block_size = 10
                total = len(item_names)
                for i in range(0, total, block_size):
                    block = item_names[i:i+block_size]
                    block_lines = [f"{i+j+1}. {name}: {data['id']}" for j, (name, data) in enumerate(block)]
                    msg = "\nSaved items:\n" + "\n".join(block_lines)
                    await self.bot.highrise.send_whisper(user.id, msg)
            else:
                await self.bot.highrise.send_whisper(user.id, "No items saved.")
        elif len(args) == 1 and args[0].lower() == "wearing":
            # List all items currently worn by the bot, whispering tag and id for each
            try:
                current = await self._get_current_outfit()
                sent = set()
                for item in current:
                    item_id = getattr(item, 'id', None)
                    item_tag = getattr(item, 'type', None)
                    # Avoid spamming duplicate ids
                    if item_id and item_id not in sent:
                        await self.bot.highrise.send_whisper(user.id, f"https://high.rs/item?id={item_id}&type={item_tag}")
                        await self.bot.highrise.send_whisper(user.id, f"{item_id}")
                        sent.add(item_id)
            except Exception as e:
                await self.bot.highrise.send_whisper(user.id, f"Failed to list currently worn items: {e}")
        else:
            await self.bot.highrise.send_whisper(user.id, "Usage: !outfit undress [item_name] | !outfit save <item_name> <item_id> | !outfit remove <item_name> | !outfit wear <item_name>|<item_id>")

    def _load_items(self):
        path = "config/outfits.json"
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_items(self, items):
        path = "config/outfits.json"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)

    async def _get_current_outfit(self):
        try:
            resp = await self.bot.highrise.get_user_outfit(self.bot.highrise.my_id)
            if hasattr(resp, "outfit"):
                return resp.outfit
            elif hasattr(resp, "items"):
                return resp.items
            else:
                return []
        except Exception:
            return []
