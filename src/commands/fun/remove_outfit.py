from highrise import User, Item
from config.config import config


# New class to remove an outfit item
class Command:
    """
    Command to remove an outfit item from the bot's outfit.
    """
    def __init__(self, bot):
        """
        Initialize the command with the bot instance.
        """
        self.bot = bot
        self.name = "remove_outfit"
        self.description = "Remove an item from the bot's outfit"
        self.permissions = ["remove_outfit"]
        self.aliases = []
        self.cooldown = 1

    async def execute(self, user: User, args: list, message: str):
        """
        Execute the command to remove an outfit item.
        
        :param user: The user who issued the command.
        :param args: The arguments passed with the command.
        :param message: The message containing the command.
        """
        if not args:
            await self.bot.highrise.chat("Please provide an outfit item ID to remove.")
            return

        item_id = args[0].strip()

        # Fetch the user's outfit
        outfit_response = await self.bot.highrise.get_my_outfit()
        outfits = outfit_response.outfit

        # Remove the item from the outfit list
        updated_outfits = [item for item in outfits if item.id != item_id]

        # Check if an item was removed
        if len(updated_outfits) == len(outfits):
            await self.bot.highrise.chat(f"No outfit item found with ID '{item_id}'.")
            return

        # Update the bot's outfit
        await self.bot.highrise.set_outfit(updated_outfits)
        await self.bot.highrise.chat(f"Outfit item with ID '{item_id}' removed successfully.")
