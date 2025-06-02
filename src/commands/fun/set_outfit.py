from highrise import User, Item
from config.config import config
from src.utility.ai import chat

COMMAND_NAME = "set_outfit"
DESCRIPTION = "Set bot outfit"
PERMISSIONS = ["set_outfit"]
ALIASES = ['speak', 'talk']
COOLDOWN = 1
MSG_PROVIDE_ITEM_ID = "Please provide an item ID."
MSG_OUTFIT_CHANGED = "\nOutfit item changed to {item_id}!"
MSG_ITEM_ADDED = "No outfit item found with prefix '{prefix}'. Added to the list."

class Command:
    """
    Command to set the bot's outfit.
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
        Execute the command to set the bot's outfit.
        
        :param user: The user who issued the command.
        :param args: The arguments passed with the command.
        :param message: The message containing the command.
        """
        if not args:
            await self.bot.highrise.chat(MSG_PROVIDE_ITEM_ID)
            return

        item_id = args[0].strip()
        prefix = item_id.split('-')[0]  # Get the prefix (e.g., 'hair_back')

        # Fetch the user's outfit
        outfit_response = await self.bot.highrise.get_my_outfit()
        outfits = outfit_response.outfit

        # Find and replace the outfit item with the new item ID
        item_found = self.update_outfit(outfits, item_id, prefix)

        if item_found:
            await self.bot.highrise.set_outfit(outfits)
            await self.bot.highrise.chat(f"\nOutfit item changed to {item_id}!")
        else:
            outfits.append(Item(type="clothing", amount=1, id=item_id, account_bound=False, active_palette=1))
            self.bot.highrise.set_outfit(outfits)
            await self.bot.highrise.chat(f"No outfit item found with prefix '{prefix}'. Added to the list.")

    def update_outfit(self, outfits, item_id, prefix):
        """
        Update the outfit list by replacing or adding an item with the given ID.
        
        :param outfits: List of current outfit items.
        :param item_id: ID of the new item to set.
        :param prefix: Prefix of the item to replace.
        :return: True if an item was replaced, False if a new item was added.
        """
        for outfit in outfits:
            if outfit.id.startswith(prefix):
                outfit.id = item_id
                return True
        return False
