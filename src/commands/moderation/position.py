from config.config import config, messages
from src.commands.command_base import CommandBase
from highrise import User, Position, AnchorPosition


class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)
        self.name = "position"
        self.description = "Display someone's position in the room."
        self.permissions = ['admin', 'moderator']
        self.aliases = ['location', 'coords', 'coordinates']
        self.cooldown = 5

    async def execute(self, user: User, args: list, message: str):
        from src.handlers.handleCommands import get_user_permissions
        user_permissions = get_user_permissions(user)
        # Allow if user has '*' (owner), 'admin', or 'owner' in permissions
        if not ("*" in user_permissions or "admin" in user_permissions or "owner" in user_permissions):
            return await self.bot.highrise.send_whisper(user.id, "This command is moderator only command")
        else:
            prefix = config.prefix
            # Get the room users
            response = await self.bot.highrise.get_room_users()
            users = [content[0]
                     for content in response.content]  # Extract the User objects
            # Extract the usernames in lowercase
            usernames = [user.username.lower() for user in users]

            # Check if the specified user is in the room
            if len(args) != 1:
                await self.bot.highrise.send_whisper(user.id, f"{messages.invalidUsage.format(prefix=prefix, commandName='print',args=' @username')}")
                return
            # Check if the lowercase version of the username is in the list
            elif args[0].startswith("@") and len(args[0]) > 1:
                # extract the username by removing the "@" symbol
                username = args[0][1:]
            else:
                username = args[0]
            if username.lower() not in usernames:
                await self.bot.highrise.send_whisper(user.id, f"{messages.invalidPlayer.format(user=username)}")
                return

            # Get the position of the specified user
            # Find the User object for the specified username
            user = users[usernames.index(username.lower())]
            position = None
            for content in response.content:
                if content[0].id == user.id:
                    if isinstance(content[1], Position):
                        position = content[1]
                        msg = f"@{user.username} is at ({position.x}x, {position.y}y, {position.z}z) facing '{position.facing}'"
                    elif isinstance(content[1], AnchorPosition):
                        position = content[1]
                        msg = f"@{user.username} is on entity: {position.entity_id} anchor: {position.anchor_ix}"
                    break

            # Print the user ID and position
            print(msg)
            await self.bot.highrise.chat(msg)
