from highrise import User

from src.utility.ai import ask_bot
from src.commands.command_base import CommandBase

class Command(CommandBase):
    """
    Command to check the bot's wallet.
    """
    def __init__(self, bot):
        """
        Initialize the wallet command with the bot instance.
        """
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        """
        Execute the wallet command.
        
        :param user: The user who issued the command.
        :param args: The arguments passed with the command.
        :param message: The message containing the command.
        """
        try:
            wallet = await self.bot.highrise.get_wallet()
            gold = self.get_gold_amount(wallet)
            items = getattr(wallet, 'items', [])
            item_list = []
            for item in items:
                if hasattr(item, 'amount') and hasattr(item, 'type'):
                    item_list.append(f"{item.amount} {item.type}")
            if gold is not None:
                msg = "Hello, {username}! My current balance is {gold} gold!".format(username=user.username, gold=gold)
                if item_list:
                    msg += " | Other items: " + ", ".join(item_list)
                await self.bot.highrise.chat(msg)
                question = "You currently have {gold} in your wallet. What is your comment to that?".format(gold=gold)
                await ask_bot(self.bot, user, question)
            else:
                await self.bot.highrise.chat("Hello, {username}! I don't have any gold.".format(username=user.username))
        except Exception as e:
            await self.bot.highrise.chat(f"An error occurred: {e}")

    def get_gold_amount(self, wallet) -> int:
        """
        Get the amount of gold from the wallet.
        
        :param wallet: The wallet object containing the items.
        :return: The amount of gold if found, None otherwise.
        """
        if hasattr(wallet, 'items'):
            for item in wallet.items:
                if hasattr(item, 'type') and item.type == 'gold':
                    return getattr(item, 'amount', 0)
        return None
