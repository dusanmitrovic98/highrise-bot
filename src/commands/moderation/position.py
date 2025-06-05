from config.config import config, messages
from src.commands.command_base import CommandBase
from highrise import User, Position, AnchorPosition


class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):
        prefix = config.prefix
        # Get the room users
        response = await self.bot.highrise.get_room_users()
        users = [content[0]
                 for content in response.content]  # Extract the User objects
        # Extract the usernames in lowercase
        usernames = [user.username.lower() for user in users]

        # If no argument, use the caller's username
        if len(args) == 0:
            username = user.username
        # Check if the specified user is in the room
        elif len(args) == 1:
            if args[0].startswith("@") and len(args[0]) > 1:
                # extract the username by removing the "@" symbol
                username = args[0][1:]
            else:
                username = args[0]
            if username.lower() not in usernames:
                await self.bot.highrise.send_whisper(user.id, f"{messages.invalidPlayer.format(user=username)}")
                return
        else:
            await self.bot.highrise.send_whisper(user.id, f"{messages.invalidUsage.format(prefix=prefix, commandName='print',args=' @username')}")
            return

        # Get the position of the specified user
        # Find the User object for the specified username
        user_obj = users[usernames.index(username.lower())]
        position = None
        for content in response.content:
            if content[0].id == user_obj.id:
                if isinstance(content[1], Position):
                    position = content[1]
                    msg = f"@{user_obj.username} is at ({position.x}x, {position.y}y, {position.z}z) facing '{position.facing}'"
                elif isinstance(content[1], AnchorPosition):
                    position = content[1]
                    msg = f"@{user_obj.username} is on entity: {position.entity_id} anchor: {position.anchor_ix}"
                break

        # Print the user ID and position
        print(msg)
        await self.bot.highrise.chat(msg)
