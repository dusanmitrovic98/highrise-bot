import asyncio
import json
import os
from venv import logger

from highrise import AnchorPosition, Position, User
from src.commands.command_base import CommandBase

EMOTES_PATH = os.path.join(os.path.dirname(__file__), '../../config/commands/emotes.json')
RESERVED = {"list", "save", "update", "remove", "details", "move", "loop", "interval", "all"}

class Command(CommandBase):
    name = "emote"
    description = "Play, list, save, update, remove, or show details for emotes. Usage: !emote <name|id|number> [loop] [interval] [all|@user ...] | !emote list | !emote save ... | !emote update ... | !emote remove ... | !emote details ... | !emote move ... | !emote stop"
    aliases = []
    cooldown = 0
    permissions = []

    # Track running emote loops per user
    emote_loops = {}

    def __init__(self, bot):
        super().__init__(bot)
        self.add_handler("on_chat", self.on_chat_handler)
        self.add_handler("on_move", self.on_move_handler)

    def _parse_kv_args(self, args):
        # Support key="value with spaces" or key=value
        import shlex
        parsed = {}
        for arg in args:
            if '=' in arg:
                k, v = arg.split('=', 1)
                if v.startswith('"') and v.endswith('"'):
                    v = v[1:-1]
                elif v.startswith("'") and v.endswith("'"):
                    v = v[1:-1]
                parsed[k] = v
        return parsed

    def _load_emotes(self):
        if not os.path.exists(EMOTES_PATH):
            return []
        with open(EMOTES_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get("emotes_free", [])

    def _save_emotes(self, emotes):
        with open(EMOTES_PATH, 'w', encoding='utf-8') as f:
            json.dump({"emotes_free": emotes}, f, indent=4)

    async def execute(self, user: User, args: list, message: str):
        emotes = self._load_emotes()
        if not args:
            await self.bot.highrise.send_whisper(user.id, "Usage: !emote <name|id|number> [loop] [interval] [all|@user ...] | !emote list | !emote save ... | !emote update ... | !emote remove ... | !emote details ... | !emote move ... | !emote stop")
            return
        cmd = args[0].lower()
        if cmd == "stop":
            # Stop emote loop for this user
            loop_task = self.emote_loops.get(user.id)
            if loop_task and not loop_task.done():
                loop_task.cancel()
                await self.bot.highrise.send_whisper(user.id, "Stopped your emote loop.")
            else:
                await self.bot.highrise.send_whisper(user.id, "No emote loop running for you.")
            return
        if cmd == "list":
            # !emote list [category_name] | !emote categories
            if len(args) > 1 and args[1].lower() == "categories":
                # List all unique categories in blocks with numbering
                categories = set()
                for e in emotes:
                    cats = e.get("category", [])
                    # Always treat as list, filter to non-empty strings, lowercase for uniqueness
                    if isinstance(cats, str):
                        cats = [cats]
                    for c in cats:
                        if isinstance(c, str):
                            c = c.strip()
                            if c:
                                categories.add(c)
                categories = sorted(categories, key=lambda x: x.lower())
                block = []
                for i, cat in enumerate(categories, 1):
                    block.append(f"{i}. {cat}")
                    if len(block) == 10 or i == len(categories):
                        await self.bot.highrise.send_whisper(user.id, "CATEGORIES:\n" + "\n".join(block))
                        block = []
                if not categories:
                    await self.bot.highrise.send_whisper(user.id, "No categories found.")
                return
            elif len(args) > 1:
                # List emotes by category
                category = args[1].strip().lower()
                filtered = [e["name"] for e in emotes if any(isinstance(c, str) and c.strip().lower() == category for c in (e.get("category", []) if isinstance(e.get("category", []), list) else [e.get("category", "")]))]
                if not filtered:
                    await self.bot.highrise.send_whisper(user.id, f"No emotes found in category '{category}'.")
                    return
                block = []
                for i, name in enumerate(filtered, 1):
                    block.append(f"{i}. {name}")
                    if len(block) == 10 or i == len(filtered):
                        await self.bot.highrise.send_whisper(user.id, f"EMOTES in '{category}':\n" + "\n".join(block))
                        block = []
                return
            else:
                # List all emotes in blocks
                names = [e["name"] for e in emotes]
                block = []
                for i, name in enumerate(names, 1):
                    block.append(f"{i}. {name}")
                    if len(block) == 10 or i == len(names):
                        await self.bot.highrise.send_whisper(user.id, "EMOTES:\n" + "\n".join(block))
                        block = []
                return
        if cmd == "save":
            # !emote save name emote_id [category=cat1,cat2,...] [interval=...]
            if len(args) < 3:
                await self.bot.highrise.send_whisper(user.id, "Usage: !emote save <name> <id> [category=cat1,cat2,...] [interval=...]")
                return
            name, emote_id = args[1], args[2]
            if name in RESERVED or any(e["name"] == name for e in emotes):
                await self.bot.highrise.send_whisper(user.id, f"Emote name '{name}' is reserved or already exists.")
                return
            kv_args = self._parse_kv_args(args[3:])
            new_emote = {"name": name, "id": emote_id}
            if "category" in kv_args:
                cats = [c.strip().lower() for c in kv_args["category"].split(",") if c.strip()]
                # Deduplicate and filter out empty
                cats = list(dict.fromkeys([c for c in cats if c]))
                new_emote["category"] = cats
            if "interval" in kv_args:
                try:
                    new_emote["interval"] = float(kv_args["interval"])
                except Exception:
                    pass
            emotes.append(new_emote)
            self._save_emotes(emotes)
            await self.bot.highrise.send_whisper(user.id, f"Emote '{name}' saved.")
            return
        if cmd == "update":
            # !emote update name [category=cat1,cat2,...] [interval=...]
            if len(args) < 2:
                await self.bot.highrise.send_whisper(user.id, "Usage: !emote update <name> [category=cat1,cat2,...] [interval=...]")
                return
            name = args[1]
            kv_args = self._parse_kv_args(args[2:])
            for emote in emotes:
                if emote["name"] == name:
                    if "category" in kv_args:
                        cats = [c.strip().lower() for c in kv_args["category"].split(",") if c.strip()]
                        cats = list(dict.fromkeys([c for c in cats if c]))
                        emote["category"] = cats
                    if "interval" in kv_args:
                        try:
                            emote["interval"] = float(kv_args["interval"])
                        except Exception:
                            pass
                    self._save_emotes(emotes)
                    await self.bot.highrise.send_whisper(user.id, f"Emote '{name}' updated.")
                    return
            await self.bot.highrise.send_whisper(user.id, f"Emote '{name}' not found.")
            return
        if cmd == "remove":
            # !emote remove name
            if len(args) < 2:
                await self.bot.highrise.send_whisper(user.id, "Usage: !emote remove <name>")
                return
            name = args[1]
            new_emotes = [e for e in emotes if e["name"] != name]
            if len(new_emotes) == len(emotes):
                await self.bot.highrise.send_whisper(user.id, f"Emote '{name}' not found.")
                return
            self._save_emotes(new_emotes)
            await self.bot.highrise.send_whisper(user.id, f"Emote '{name}' removed.")
            return
        if cmd == "details":
            # !emote details name|number
            if len(args) < 2:
                await self.bot.highrise.send_whisper(user.id, "Usage: !emote details <name|number>")
                return
            key = args[1]
            emote = None
            if key.isdigit():
                idx = int(key) - 1
                if 0 <= idx < len(emotes):
                    emote = emotes[idx]
            else:
                for e in emotes:
                    if e["name"] == key:
                        emote = e
                        break
            if not emote:
                await self.bot.highrise.send_whisper(user.id, f"Emote '{key}' not found.")
                return
            cats = emote.get('category', [])
            if isinstance(cats, str):
                cats = [cats]
            cats = [c for c in cats if isinstance(c, str) and c.strip()]
            details = f"Name: {emote['name']}\nId: {emote['id']}\nCategories: {', '.join(cats)}\nInterval: {emote.get('interval', 10)}"
            await self.bot.highrise.send_whisper(user.id, details)
            return
        if cmd == "move":
            # !emote move emote_name position_index
            if len(args) < 3 or not args[2].isdigit():
                await self.bot.highrise.send_whisper(user.id, "Usage: !emote move <name> <position_index>")
                return
            name, idx = args[1], int(args[2])
            for i, emote in enumerate(emotes):
                if emote["name"] == name:
                    if idx < 1 or idx > len(emotes):
                        await self.bot.highrise.send_whisper(user.id, f"Position index must be between 1 and {len(emotes)}.")
                        return
                    em = emotes.pop(i)
                    emotes.insert(idx-1, em)
                    self._save_emotes(emotes)
                    await self.bot.highrise.send_whisper(user.id, f"Emote '{name}' moved to position {idx}.")
                    return
            await self.bot.highrise.send_whisper(user.id, f"Emote '{name}' not found.")
            return
        # Stop emote loop for this user if running before playing a new emote
        loop_task = self.emote_loops.get(user.id)
        if loop_task and not loop_task.done():
            loop_task.cancel()
            await self.bot.highrise.send_whisper(user.id, "Stopped your previous emote loop.")
        # Play emote logic: by number, name, or id
        loop = False
        interval = None
        targets = []
        for arg in args[1:]:
            if arg == "loop":
                loop = True
            elif arg.startswith("interval="):
                try:
                    interval = float(arg.split("=", 1)[1])
                except Exception:
                    pass
            elif arg == "all":
                targets.append("all")
            elif arg.startswith("@"):
                targets.append(arg[1:])
        # Find emote by number, name, or id
        emote = None
        if cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(emotes):
                emote = emotes[idx]
        else:
            for e in emotes:
                if e["name"].lower() == cmd or e["id"] == cmd:
                    emote = e
                    break
        if not emote:
            # Try to find by first keyword in message
            for e in emotes:
                if e["name"] in message:
                    emote = e
                    break
        if not emote:
            await self.bot.highrise.send_whisper(user.id, f"Emote '{cmd}' not found.")
            return
        # Determine interval
        use_interval = interval if interval is not None else emote.get("interval", 3)
        # Determine targets
        user_ids = []
        if "all" in targets:
            users_resp = await self.bot.highrise.get_room_users()
            if hasattr(users_resp, 'content'):
                user_ids = [u.id for u, _ in users_resp.content if u.id != self.bot.highrise.my_id]
        elif targets:
            users_resp = await self.bot.highrise.get_room_users()
            if hasattr(users_resp, 'content'):
                for u, _ in users_resp.content:
                    if u.username.lower() in [t.lower() for t in targets]:
                        user_ids.append(u.id)
        else:
            user_ids = [user.id]
        # Play emote(s)
        async def play_emote_loop(target_id):
            try:
                while True:
                    await self.bot.highrise.send_emote(emote["id"], target_id)
                    await asyncio.sleep(use_interval)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                # Optionally log the error or notify the user
                logger.error(f"Error in emote loop for {target_id}: {e}")
                await self.bot.highrise.send_whisper(target_id, "Emote loop stopped due to error.")
            finally:
                # Clean up reference after loop ends
                if self.emote_loops.get(target_id):
                    del self.emote_loops[target_id]
        if loop:
            for uid in user_ids:
                task = asyncio.create_task(play_emote_loop(uid))
                self.emote_loops[uid] = task
            await self.bot.highrise.send_whisper(user.id, f"Looping emote '{emote['name']}' for {', '.join(user_ids)}.")
        else:
            for uid in user_ids:
                await self.bot.highrise.send_emote(emote["id"], uid)
            await self.bot.highrise.send_whisper(user.id, f"Played emote '{emote['name']}' for {', '.join(user_ids)}.")

    async def on_chat_handler(self, user: User, message: str):
        emotes = self._load_emotes()
        msg = message.strip()
        lower_msg = msg.lower()
        # Stop loop if user says 'stop'
        if lower_msg == "stop":
            loop_task = self.emote_loops.get(user.id)
            if loop_task and not loop_task.done():
                loop_task.cancel()
                await self.bot.highrise.send_whisper(user.id, "Stopped your emote loop.")
            else:
                await self.bot.highrise.send_whisper(user.id, "No emote loop running for you.")
            return
        # Parse for loop/interval
        parts = msg.split()
        loop = False
        interval = None
        for p in parts[1:]:
            if p == "loop":
                loop = True
            elif p.startswith("interval="):
                try:
                    interval = float(p.split("=", 1)[1])
                except Exception:
                    pass
        # Find emote by number, name, or id
        emote = None
        if parts[0].isdigit():
            idx = int(parts[0]) - 1
            if 0 <= idx < len(emotes):
                emote = emotes[idx]
        else:
            for e in emotes:
                if e["name"].lower() in lower_msg or e["id"] == parts[0]:
                    emote = e
                    break
        if emote:
            use_interval = interval if interval is not None else emote.get("interval", 3)
            # Stop emote loop for this user if running before starting a new loop
            if loop:
                loop_task = self.emote_loops.get(user.id)
                if loop_task and not loop_task.done():
                    loop_task.cancel()
                    await self.bot.highrise.send_whisper(user.id, "Stopped your previous emote loop.")
            async def play_emote_loop():
                try:
                    while True:
                        await self.bot.highrise.send_emote(emote["id"], user.id)
                        await asyncio.sleep(use_interval)
                except asyncio.CancelledError:
                    pass
            if loop:
                task = asyncio.create_task(play_emote_loop())
                self.emote_loops[user.id] = task
                await self.bot.highrise.send_whisper(user.id, f"Looping emote '{emote['name']}' for you.")
            else:
                # Stop emote loop for this user if running before playing a new emote
                loop_task = self.emote_loops.get(user.id)
                if loop_task and not loop_task.done():
                    loop_task.cancel()
                    await self.bot.highrise.send_whisper(user.id, "Stopped your previous emote loop.")
                await self.bot.highrise.send_emote(emote["id"], user.id)
    
    async def on_move_handler(self, user: User, destination: Position | AnchorPosition):
        # Stop emote loop for this user if running
        loop_task = self.emote_loops.get(user.id)
        if loop_task and not loop_task.done():
            loop_task.cancel()
            await self.bot.highrise.send_whisper(user.id, "Stopped your emote loop due to move.")
