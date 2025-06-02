from highrise import User

from src.utility.ai import ask_bot

COMMAND_NAME = "wallet"
COMMAND_DESCRIPTION = "Check the bot's wallet"
COMMAND_COOLDOWN = 5
MSG_NO_GOLD = "Hello, {username}! I don't have any gold."
MSG_BALANCE = "Hello, {username}! My current balance is {gold} gold!"
QUESTION_COMMENT = "You currently have {gold} in your wallet. What is your comment to that?"

class Command:
    """
    Command to check the bot's wallet.
    """
    def __init__(self, bot):
        """
        Initialize the wallet command with the bot instance.
        """
        self.bot = bot
        self.name = COMMAND_NAME
        self.description = COMMAND_DESCRIPTION
        self.cooldown = COMMAND_COOLDOWN

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
                msg = MSG_BALANCE.format(username=user.username, gold=gold)
                if item_list:
                    msg += " | Other items: " + ", ".join(item_list)
                await self.bot.highrise.chat(msg)
                question = QUESTION_COMMENT.format(gold=gold)
                await ask_bot(self.bot, user, question)
            else:
                await self.bot.highrise.chat(MSG_NO_GOLD.format(username=user.username))
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
