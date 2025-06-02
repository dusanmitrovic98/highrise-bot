from highrise import User
from config.config import config
from src.utility.ai import ask_bot

COMMAND_NAME = "follow_user"
DESCRIPTION = "Makes the bot follow a user."
PERMISSIONS = ["follow_user"]
ALIASES = ['followme', 'follow']
COOLDOWN = 10

class Command:
    """
    Command to make the bot follow a user.
    """
    def __init__(self, bot):
        self.bot = bot
        self.name = COMMAND_NAME
        self.description = DESCRIPTION
        self.permissions = PERMISSIONS
        self.aliases = ALIASES
        self.cooldown = COOLDOWN

    async def execute(self, user: User, args: list, message: str):
        """
        Execute the command to make the bot follow a user by username or the command issuer.
        """
        target_user = user
        if args and args[0].startswith("@"):
            username = args[0][1:].lower()
            response = await self.bot.highrise.get_room_users()
            users = [content[0] for content in response.content]
            match = next((u for u in users if u.username.lower() == username), None)
            if not match:
                await self.bot.highrise.send_whisper(user.id, f"User '{username}' not found in the room.")
                return
            target_user = match
        config.follow_user_id = target_user.id
        await self.follow_user(target_user)

    async def follow_user(self, user: User):
        """
        Logic to make the bot follow the user.
        """
        question = f"I am now following you, {user.username}! Where to?"
        await ask_bot(self.bot, user, question)
