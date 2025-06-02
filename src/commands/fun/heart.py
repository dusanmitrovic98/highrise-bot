from highrise import User
from config.config import config

COMMAND_NAME = "heart"
DESCRIPTION = "Send a heart emote to a user or everyone in the room."
PERMISSIONS = ["emote"]
ALIASES = ["love", "sendheart"]
COOLDOWN = 5
HEART_EMOTE = "emoji-thumbsup"  # Changed to a free/owned emote. Replace with a valid heart emote if available.

class Command:
    """
    Command to send a heart emote to a user or all users in the room.
    """
    def __init__(self, bot):
        self.bot = bot
        self.name = COMMAND_NAME
        self.description = DESCRIPTION
        self.permissions = PERMISSIONS
        self.aliases = ALIASES
        self.cooldown = COOLDOWN

    async def execute(self, user: User, args: list, message: str):
        if args and args[0].lower() == "all":
            response = await self.bot.highrise.get_room_users()
            users = [content[0] for content in response.content]
            failed = []
            for target in users:
                try:
                    await self.bot.highrise.send_emote(HEART_EMOTE, target.id)
                except Exception:
                    failed.append(target.username)
            if failed:
                await self.bot.highrise.chat(f"Could not send heart to: {', '.join(failed)} (emote not owned)")
            else:
                await self.bot.highrise.chat("Sent a heart to everyone in the room!")
        else:
            target_user = user
            if args:
                username = args[0].lstrip("@").lower()
                response = await self.bot.highrise.get_room_users()
                users = [content[0] for content in response.content]
                match = next((u for u in users if u.username.lower() == username), None)
                if not match:
                    await self.bot.highrise.send_whisper(user.id, f"User '{username}' not found in the room.")
                    return
                target_user = match
            try:
                await self.bot.highrise.send_emote(HEART_EMOTE, target_user.id)
                await self.bot.highrise.chat(f"Sent a heart to @{target_user.username}!")
            except Exception:
                await self.bot.highrise.send_whisper(user.id, f"Could not send heart to @{target_user.username}: emote not owned or not free.")
