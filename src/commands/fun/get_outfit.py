from highrise import User
from config.config import config
from src.utility.ai import ask_bot, chat

COMMAND_NAME = "get_outfit"
DESCRIPTION = "Get bot outfit"
PERMISSIONS = ["get_outfit"]
ALIASES = ['speak', 'talk']
COOLDOWN = 1
RESPONSE_MAX_LENGTH = 252

class Command:
    """
    Command to get the bot's outfit and display it.
    """
    def __init__(self, bot):
        """
        Initialize the command with the bot instance.
        """
        self.bot = bot
        self.name = COMMAND_NAME
        self.description = DESCRIPTION
        self.permissions = PERMISSIONS
        self.aliases = ALIASES
        self.cooldown = COOLDOWN

    async def execute(self, user: User, args: list, message: str):
        """
        Execute the command to get the bot's outfit.
        
        :param user: The user who issued the command.
        :param args: The arguments passed with the command.
        :param message: The message containing the command.
        """
        prefix = config.prefix
        message = message.replace(f"{prefix}{COMMAND_NAME}", "").strip()
        
        outfit_response = await self.bot.highrise.get_my_outfit()
        outfit_items = outfit_response.outfit

        print(f"number_of_items: {len(outfit_items)}")

        bot_response_message = self.build_response_message(outfit_items)

        bot_response_message_first_part = bot_response_message[:RESPONSE_MAX_LENGTH] + "..."
        await self.bot.highrise.chat(bot_response_message_first_part)

        bot_response_message_second_part = "..." + bot_response_message[RESPONSE_MAX_LENGTH:]
        await self.bot.highrise.chat(bot_response_message_second_part)

        await ask_bot(self.bot, user, "I just checked what you are wearing what do u have to say on that?")

    def build_response_message(self, outfit_items):
        """
        Build the response message from the outfit items.
        
        :param outfit_items: List of outfit items.
        :return: Response message as a string.
        """
        return "\n" + "\n".join(item.id for item in outfit_items)
