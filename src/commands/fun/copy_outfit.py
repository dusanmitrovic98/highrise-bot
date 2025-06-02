from highrise import User, Item
from config.config import config, messages

COMMAND_NAME = "copy"
DESCRIPTION = "Copy the outfit of another user."
PERMISSIONS = ["set_outfit"]
ALIASES = ["copyoutfit", "stealoutfit"]
COOLDOWN = 5

class Command:
    """
    Command to copy the outfit of another user in the room.
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
            await self.bot.highrise.send_whisper(user.id, "Usage: /copy @username or /copy <user_id> or /copy !<webapi_user_id>")
            return
        arg = args[0]
        # Allow @username (room only), user_id (API), !user_id (webapi)
        if arg.startswith("@"):  # Username in room
            await self.bot.highrise.send_whisper(user.id, "Copying by username only works for users in the room. Use user ID for global copy.")
            username = arg[1:].lower()
            response = await self.bot.highrise.get_room_users()
            users = [content[0] for content in response.content]
            match = next((u for u in users if u.username.lower() == username), None)
            if not match:
                await self.bot.highrise.send_whisper(user.id, f"User '{username}' not found in the room.")
                return
            target_user_id = match.id
            try:
                outfit_response = await self.bot.highrise.get_user_outfit(target_user_id)
                outfit_items = outfit_response.outfit
                print(f"Outfit for user {arg}:")
                for item in outfit_items:
                    print(item)
                await self.bot.highrise.set_outfit(outfit_items)
                await self.bot.highrise.chat(f"Copied outfit from user {arg}!")
            except Exception as e:
                await self.bot.highrise.send_whisper(user.id, f"Failed to copy outfit: {e}")
        elif arg.startswith("!"):  # WebAPI user id
            webapi_user_id = arg[1:]
            try:
                user_info = await self.bot.webapi.get_user(webapi_user_id)
                print(user_info)
                # Try to use user_info.user.outfit if present
                if hasattr(user_info.user, "outfit") and user_info.user.outfit:
                    # Convert webapi outfit items to Item objects, supporting both dict and object types
                    outfit_items = []
                    for item in user_info.user.outfit:
                        if isinstance(item, dict):
                            item_id = item["item_id"]
                            active_palette = item.get("active_palette", 1)
                        else:
                            item_id = getattr(item, "item_id", None)
                            active_palette = getattr(item, "active_palette", 1)
                        if item_id:
                            outfit_items.append(Item(
                                type="clothing",
                                amount=1,
                                id=item_id,
                                account_bound=False,
                                active_palette=active_palette
                            ))
                    print(f"Outfit for webapi user {webapi_user_id} (from webapi):")
                    for item in outfit_items:
                        print(item)
                    await self.bot.highrise.set_outfit(outfit_items)
                    await self.bot.highrise.chat(f"Copied outfit from webapi user {webapi_user_id}!")
                else:
                    # Fallback to get_user_outfit if no outfit in webapi
                    outfit_response = await self.bot.highrise.get_user_outfit(user_info.user.id)
                    outfit_items = outfit_response.outfit
                    print(f"Outfit for webapi user {webapi_user_id} (from get_user_outfit):")
                    for item in outfit_items:
                        print(item)
                    await self.bot.highrise.set_outfit(outfit_items)
                    await self.bot.highrise.chat(f"Copied outfit from webapi user {webapi_user_id}!")
            except Exception as e:
                await self.bot.highrise.send_whisper(user.id, f"Failed to copy outfit from webapi: {e}")
        else:  # Assume user_id (API)
            target_user_id = arg
            try:
                outfit_response = await self.bot.highrise.get_user_outfit(target_user_id)
                outfit_items = outfit_response.outfit
                print(f"Outfit for user {arg}:")
                for item in outfit_items:
                    print(item)
                await self.bot.highrise.set_outfit(outfit_items)
                await self.bot.highrise.chat(f"Copied outfit from user {arg}!")
            except Exception as e:
                await self.bot.highrise.send_whisper(user.id, f"Failed to copy outfit: {e}")
