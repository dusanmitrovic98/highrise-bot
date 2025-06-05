from config.config import get_section
from src.commands.command_base import CommandBase

class Command(CommandBase):
    """
    Command to warp a user (or yourself) to a room using a portal name or room ID.
    Usage:
      !portal <room_name_or_id>
      !warp <room_name_or_id>
    """
    def __init__(self, bot):
        super().__init__(bot)
        self.aliases = ["warp"]

    async def execute(self, user, args, message):
        if not args:
            await self.bot.highrise.send_whisper(user.id, "Usage: !portal <room_name_or_id> [@username] | !portal all <room_name_or_id>")
            return
        portals = get_section("portals") or {}
        # Mass teleport: !portal all <dest>
        if args[0].lower() == "all" and len(args) > 1:
            key = args[1]
            room_id = portals.get(key, key if len(key) == 24 else None)
            if not room_id:
                await self.bot.highrise.send_whisper(user.id, f"No portal named '{key}' and not a valid room ID.")
                return
            users_resp = await self.bot.highrise.get_room_users()
            bot_id = None
            from config.config import get
            bot_id = get('bot_id')
            bot_name = get('bot_name')
            if hasattr(users_resp, 'content'):
                count = 0
                for u, _ in users_resp.content:
                    try:
                        if u.id == bot_id:
                            continue  # Warp bot after all users
                        await self.bot.highrise.move_user_to_room(u.id, room_id)
                        count += 1
                    except Exception:
                        pass
                await self.bot.highrise.send_whisper(user.id, f"Warped {count} users to room '{key}'.")
                # Now warp the bot itself: save room_id into runtime/flags/warp.flag
                import os
                flag_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'runtime', 'flags')
                os.makedirs(flag_dir, exist_ok=True)
                flag_path = os.path.join(flag_dir, 'warp.flag')
                with open(flag_path, 'w') as f:
                    f.write(room_id)
                await self.bot.highrise.send_whisper(user.id, f"Bot is now moving to room '{key}' and will restart.")
                os._exit(1)
            else:
                await self.bot.highrise.send_whisper(user.id, "Could not fetch room users.")
            return
        # Check for user mention as second argument
        if len(args) > 1 and args[1].startswith("@"):
            username = args[1][1:]
            from config.config import get
            bot_id = get('bot_id')
            bot_name = get('bot_name')
            if bot_name and username.lower() == bot_name.lower():
                # Instead of move_user_to_room, use the same logic as warp all for the bot
                import os
                flag_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'runtime', 'flags')
                os.makedirs(flag_dir, exist_ok=True)
                flag_path = os.path.join(flag_dir, 'warp.flag')
                key = args[0]
                room_id = portals.get(key, key if len(key) == 24 else None)
                if not room_id:
                    await self.bot.highrise.send_whisper(user.id, f"No portal named '{key}' and not a valid room ID.")
                    return
                with open(flag_path, 'w') as f:
                    f.write(room_id)
                await self.bot.highrise.send_whisper(user.id, f"Bot is now moving to room '{key}' and will restart.")
                os._exit(1)
            else:
                users_resp = await self.bot.highrise.get_room_users()
                if hasattr(users_resp, 'content'):
                    found = False
                    for u, _ in users_resp.content:
                        if u.username.lower() == username.lower():
                            target_user = u
                            found = True
                            break
                    if not found:
                        await self.bot.highrise.send_whisper(user.id, f"User @{username} not found in the room.")
                        return
                    key = args[0]
                    room_id = portals.get(key, key if len(key) == 24 else None)
                    if not room_id:
                        await self.bot.highrise.send_whisper(user.id, f"No portal named '{key}' and not a valid room ID.")
                        return
                else:
                    await self.bot.highrise.send_whisper(user.id, "Could not fetch room users.")
                    return
        else:
            target_user = user
            key = args[0]
            room_id = portals.get(key, key if len(key) == 24 else None)
            if not room_id:
                await self.bot.highrise.send_whisper(user.id, f"No portal named '{key}' and not a valid room ID.")
                return
        try:
            if 'target_user' in locals():
                await self.bot.highrise.move_user_to_room(target_user.id, room_id)
                if target_user.id == user.id:
                    await self.bot.highrise.send_whisper(user.id, f"Warping you to room '{key}'.")
                else:
                    await self.bot.highrise.send_whisper(user.id, f"Warping @{target_user.username} with id {target_user.id} to room '{key}'.")
        except Exception as exc:
            await self.bot.highrise.send_whisper(user.id, f"Failed to warp: {exc}")
