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

    async def execute(self, user, args, message):
        if args and args[0].lower() == "list":
            # Show available emotes from config/json/emotes.json
            emotes_path = os.path.join(os.path.dirname(__file__), '../../../../config/json/emotes.json')
            try:
                with open(emotes_path, 'r', encoding='utf-8') as f:
                    emotes = json.load(f)
                emote_list = ', '.join(emotes[:30])  # Show first 30 for brevity
                await self.bot.highrise.chat(f"Available emotes: {emote_list} ...")
            except Exception:
                await self.bot.highrise.chat("Could not load emote list.")
            return
        if not args:
            await self.bot.highrise.chat("Usage: !emote <emote_id> [@target_user] or !emote list")
            return
        emote_id = args[0]
        target_user_id = None
        if len(args) > 1 and args[1].startswith("@"):
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
