from src.commands.command_base import CommandBase
import json
import os

class Command(CommandBase):
    """
    Command to perform an emote using the Highrise SDK.
    Usage: !emote <emote_id> [@target_user] or !emote list
    Example: !emote emote-hello @username
    """
    def __init__(self, bot):
        super().__init__(bot)
        self._looping = False
        self._loop_task = None
        self._last_emote = None

    async def execute(self, user, args, message):
        import asyncio
        if args and args[0].lower() == "list":
            # Show available emotes from config/json/emotes.json
            emotes_path = os.path.join(os.path.dirname(__file__), '../../../../config/json/emotes.json')
            try:
                with open(emotes_path, 'r', encoding='utf-8') as f:
                    emotes = json.load(f)
            except Exception:
                await self.bot.highrise.chat("Could not load emote list.")
                return
            emote_lines = [f"{i+1}. {emote} | {emote} loop" for i, emote in enumerate(emotes)]
            emote_list = "\n".join(emote_lines[:30])  # Show first 30 for brevity
            await self.bot.highrise.chat(f"Available emotes (first 30):\n{emote_list}\n...\nYou can use: !emote <number>, !emote <emote-name> loop, !emote stop loop")
            return
        if not args:
            await self.bot.highrise.chat("Usage: !emote <emote_id> [@target_user] or !emote list")
            return
        emotes_path = os.path.join(os.path.dirname(__file__), '../../../../config/json/emotes.json')
        try:
            with open(emotes_path, 'r', encoding='utf-8') as f:
                emotes = json.load(f)
        except Exception:
            emotes = []
        # Stop loop
        if args[0].lower() == "stop" and len(args) > 1 and args[1].lower() == "loop":
            self._looping = False
            if self._loop_task:
                self._loop_task.cancel()
                self._loop_task = None
            await self.bot.highrise.chat("Stopped emote loop.")
            return
        # Loop mode
        if len(args) >= 2 and args[1].lower() == "loop":
            emote_id = args[0]
            if emote_id.isdigit():
                idx = int(emote_id) - 1
                if 0 <= idx < len(emotes):
                    emote_id = emotes[idx]
                else:
                    await self.bot.highrise.chat("Invalid emote number.")
                    return
            elif emote_id not in emotes:
                await self.bot.highrise.chat(f"Emote '{emote_id}' not found.")
                return
            self._looping = True
            self._last_emote = emote_id
            if self._loop_task:
                self._loop_task.cancel()
            async def loop_emote():
                while self._looping:
                    await self.bot.highrise.send_emote(emote_id)
                    await asyncio.sleep(2.5)
            self._loop_task = asyncio.create_task(loop_emote())
            await self.bot.highrise.chat(f"Looping emote '{emote_id}'. Use !emote stop loop to stop.")
            return
        # Emote by number
        emote_id = args[0]
        if emote_id.isdigit():
            idx = int(emote_id) - 1
            if 0 <= idx < len(emotes):
                emote_id = emotes[idx]
            else:
                await self.bot.highrise.chat("Invalid emote number.")
                return
        elif emote_id not in emotes:
            await self.bot.highrise.chat(f"Emote '{emote_id}' not found.")
            return
        target_user_id = None
        if len(args) > 1 and args[1].startswith("@"):  # target user
            username = args[1][1:]
            users = await self.bot.highrise.get_room_users()
            users = users.content
            # users is a list of tuples (User, Position), so unpack User
            for u in users:
                user_obj = u[0] if isinstance(u, tuple) else u
                if hasattr(user_obj, "username") and user_obj.username.lower() == username.lower():
                    target_user_id = user_obj.id
                    break
            if not target_user_id:
                await self.bot.highrise.chat(f"User {args[1]} not found in the room.")
                return
        await self.bot.highrise.send_emote(emote_id, target_user_id)
        await self.bot.highrise.chat(f"Emote '{emote_id}' performed!" + (f" Target: {args[1]}" if target_user_id else ""))
