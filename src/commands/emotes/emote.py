from src.commands.command_base import CommandBase
import highrise
import json
import os
import asyncio


class Command(CommandBase):
    """
    Command to perform an emote using the Highrise SDK.
    Usage: !emote <emote_id> or !emote list
    """

    _emote_loop_tasks = {}

    def __init__(self, bot):
        super().__init__(bot)
        self.emotes = self._load_emotes()

    def _load_emotes(self):
        emotes_path = os.path.join(os.path.dirname(__file__), '../../../config/json/emotes.json')
        with open(emotes_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # emotes_free is a list of emote dicts
        return data.get('emotes_free', [])

    def _find_emote(self, query):
        # Try by id, then by name (case-insensitive), then by index
        for emote in self.emotes:
            if emote['id'] == query:
                return emote
            if emote['name'].lower() == query.lower():
                return emote
        # Try by index (1-based or 0-based)
        try:
            idx = int(query)
            if 1 <= idx <= len(self.emotes):
                return self.emotes[idx-1]
            elif 0 <= idx < len(self.emotes):
                return self.emotes[idx]
        except Exception:
            pass
        return None

    async def _emote_loop(self, user, emote_id, target_user_id=None, interval=3.5):
        print(f"[EMOTE LOOP] Starting emote loop: emote_id={emote_id}, target_user_id={target_user_id}, interval={interval}")
        while True:
            print(f"[EMOTE LOOP] Performing emote: {emote_id}")
            await self.bot.highrise.send_emote(emote_id, target_user_id)
            await asyncio.sleep(interval)

    async def execute(self, user, args, message):
        if not args:
            await self.bot.highrise.chat("Usage: !emote <emote_id|emote_name|number|list|stop> [loop] [@username] [interval]")
            return
        arg = args[0].lower()
        if arg == 'list':
            emote_list = [f"{i+1}. {e['name']} ({e['id']})" for i, e in enumerate(self.emotes)]
            msg = "Available emotes:\n" + "\n".join(emote_list)
            await self.bot.highrise.send_whisper(user.id, msg)
            return
        if arg == 'stop':
            task = self._emote_loop_tasks.pop(user.id, None)
            if task:
                task.cancel()
                await self.bot.highrise.send_whisper(user.id, "Stopped emote loop.")
            else:
                await self.bot.highrise.send_whisper(user.id, "No emote loop running.")
            return
        # Parse emote, loop, target, and interval
        loop_mode = 'loop' in [a.lower() for a in args]
        target_user_id = None
        interval = 3.5
        for a in args:
            if a.startswith('@'):
                target_user_id = a[1:]
            # Allow interval as a float argument
            try:
                val = float(a)
                if 0.5 <= val <= 10:
                    interval = val
            except Exception:
                pass
        if not target_user_id:
            target_user_id = user.id
        emote_query = arg
        if emote_query == 'loop':
            emote_query = args[1] if len(args) > 1 else None
        emote = self._find_emote(emote_query)
        if not emote:
            emote_id = emote_query
            print(f"[EMOTE] Performing emote (not in list): {emote_id}")
            if loop_mode:
                task = self._emote_loop_tasks.pop(user.id, None)
                if task:
                    task.cancel()
                loop_task = asyncio.create_task(self._emote_loop(user, emote_id, target_user_id, interval))
                self._emote_loop_tasks[user.id] = loop_task
                await self.bot.highrise.send_whisper(user.id, f"Started looping emote: {emote_id} (not in list) with interval {interval}s")
            else:
                await self.bot.highrise.send_emote(emote_id, target_user_id)
                await self.bot.highrise.send_whisper(user.id, f"Performed emote: {emote_id} (not in list)")
            return
        emote_id = emote['id']
        print(f"[EMOTE] Performing emote: {emote_id}")
        if loop_mode:
            # Stop previous loop if any
            task = self._emote_loop_tasks.pop(user.id, None)
            if task:
                task.cancel()
            loop_task = asyncio.create_task(self._emote_loop(user, emote_id, target_user_id, interval))
            self._emote_loop_tasks[user.id] = loop_task
            await self.bot.highrise.send_whisper(user.id, f"Started looping emote: {emote['name']} ({emote_id}) with interval {interval}s")
        else:
            await self.bot.highrise.send_emote(emote_id, target_user_id)
            await self.bot.highrise.send_whisper(user.id, f"Performed emote: {emote['name']}")
