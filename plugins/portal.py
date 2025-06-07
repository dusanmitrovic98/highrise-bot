from config.config import get_section
from src.commands.command_base import CommandBase

class Command(CommandBase):
    """
    Command to warp a user (or yourself) to a room using a portal name or room ID.
    Usage:
      !portal <room_name_or_id>
      !warp <room_name_or_id>
      !portal <room_name_or_id> all
      !portal <room_name_or_id> @user1 @user2 ...
    """
    def __init__(self, bot):
        super().__init__(bot)
        self.aliases = ["warp"]

    async def execute(self, user, args, message):
        if not args:
            await self.bot.highrise.send_whisper(user.id, "Usage: !portal <room_name_or_id> [all|@username ...]")
            return
        portals = get_section("portals") or {}
        key = args[0]
        room_id = portals.get(key, key if len(key) == 24 else None)
        if not room_id:
            await self.bot.highrise.send_whisper(user.id, f"No portal named '{key}' and not a valid room ID.")
            return
        # Check for 'all' or user mentions in the rest of the args
        if any(arg.lower() == "all" for arg in args[1:]):
            users_resp = await self.bot.highrise.get_room_users()
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
                # Send whisper BEFORE exit
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
        # Handle user mentions
        mentioned_usernames = [arg[1:] for arg in args[1:] if arg.startswith("@")]
        if mentioned_usernames:
            from config.config import get
            bot_name = get('bot_name')
            users_resp = await self.bot.highrise.get_room_users()
            if not hasattr(users_resp, 'content'):
                await self.bot.highrise.send_whisper(user.id, "Could not fetch room users.")
                return
            moved = []
            not_found = []
            for username in mentioned_usernames:
                if bot_name and username.lower() == bot_name.lower():
                    # Warp bot itself
                    import os
                    flag_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'runtime', 'flags')
                    os.makedirs(flag_dir, exist_ok=True)
                    flag_path = os.path.join(flag_dir, 'warp.flag')
                    with open(flag_path, 'w') as f:
                        f.write(room_id)
                    # Send whisper BEFORE exit
                    await self.bot.highrise.send_whisper(user.id, f"Bot is now moving to room '{key}' and will restart.")
                    os._exit(1)
                found = False
                for u, _ in users_resp.content:
                    if u.username.lower() == username.lower():
                        try:
                            await self.bot.highrise.move_user_to_room(u.id, room_id)
                            moved.append(f"@{u.username}")
                        except Exception as exc:
                            not_found.append(f"@{u.username} (error: {exc})")
                        found = True
                        break
                if not found:
                    not_found.append(f"@{username}")
            if moved:
                await self.bot.highrise.send_whisper(user.id, f"Warped {', '.join(moved)} to room '{key}'.")
            if not_found:
                await self.bot.highrise.send_whisper(user.id, f"Could not warp {', '.join(not_found)}.")
            return
        # Default: warp sender
        try:
            await self.bot.highrise.move_user_to_room(user.id, room_id)
            await self.bot.highrise.send_whisper(user.id, f"Warping you to room '{key}'.")
        except Exception as exc:
            await self.bot.highrise.send_whisper(user.id, f"Failed to warp: {exc}")
