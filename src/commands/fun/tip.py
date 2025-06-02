from highrise import User

COMMAND_NAME = "tip"
DESCRIPTION = "Tip a user a specified amount of gold. Usage: /tip @username amount"
PERMISSIONS = ["tip"]
ALIASES = ["sendtip"]
COOLDOWN = 5

class Command:
    """
    Command to tip a user a specified amount of gold.
    """
    def __init__(self, bot):
        self.bot = bot
        self.name = COMMAND_NAME
        self.description = DESCRIPTION
        self.permissions = PERMISSIONS
        self.aliases = ALIASES
        self.cooldown = COOLDOWN

    async def execute(self, user: User, args: list, message: str):
        if len(args) < 2:
            await self.bot.highrise.send_whisper(user.id, "Usage: /tip @username amount")
            return
        username = args[0].lstrip("@").lower()
        try:
            amount = int(args[1])
            if amount <= 0:
                raise ValueError
        except ValueError:
            await self.bot.highrise.send_whisper(user.id, "Please specify a valid amount of gold to tip.")
            return
        response = await self.bot.highrise.get_room_users()
        users = [content[0] for content in response.content]
        match = next((u for u in users if u.username.lower() == username), None)
        if not match:
            await self.bot.highrise.send_whisper(user.id, f"User '{username}' not found in the room.")
            return
        try:
            await self.bot.highrise.tip_user(match.id, amount)
            await self.bot.highrise.chat(f"{user.username} tipped @{match.username} {amount} gold!")
        except Exception as e:
            await self.bot.highrise.send_whisper(user.id, f"Could not tip @{match.username}: {e}")
