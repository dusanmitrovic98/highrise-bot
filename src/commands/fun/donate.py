from highrise import User

COMMAND_NAME = "donate"
DESCRIPTION = "Donate a specified amount of gold to the bot. Usage: /donate amount"
PERMISSIONS = []
ALIASES = ["givegold", "donategold"]
COOLDOWN = 5

class Command:
    """
    Command to donate gold to the bot.
    """
    def __init__(self, bot):
        self.bot = bot
        self.name = COMMAND_NAME
        self.description = DESCRIPTION
        self.permissions = PERMISSIONS
        self.aliases = ALIASES
        self.cooldown = COOLDOWN

    async def execute(self, user: User, args: list, message: str):
        if not args:
            await self.bot.highrise.send_whisper(user.id, "Usage: /donate amount")
            return
        try:
            amount = int(args[0])
            if amount <= 0:
                raise ValueError
        except ValueError:
            await self.bot.highrise.send_whisper(user.id, "Please specify a valid amount of gold to donate.")
            return
        try:
            await self.bot.highrise.receive_tip(user.id, amount)
            await self.bot.highrise.chat(f"Thank you @{user.username} for donating {amount} gold to the bot!")
        except Exception as e:
            await self.bot.highrise.send_whisper(user.id, f"Could not process donation: {e}")
