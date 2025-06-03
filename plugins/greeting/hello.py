class Command:
    name = "hello"
    aliases = ["hi"]
    permissions = []  # Or specify required permissions
    cooldown = 5  # seconds

    def __init__(self, bot):
        self.bot = bot

    async def execute(self, user, args, message):
        await self.bot.highrise.send_whisper(user.id, f"Hello, {user.username}!")