from highrise import User, Position
from config.config import messages
import asyncio
from src.commands.command_base import CommandBase
from collections import deque
import time


class Command(CommandBase):
    def __init__(self, bot):
        super().__init__(bot)

    async def execute(self, user: User, args: list, message: str):

        if not args:
            await self.bot.highrise.chat("Usage: !swap @user1 [@user2]")
            return

        def extract_username(arg):
            return arg.lstrip("@")

        usernames = [extract_username(arg) for arg in args if arg.startswith("@")]
        if not usernames:
            await self.bot.highrise.chat("Please mention at least one user to swap with.")
            return

        await self.bot.highrise.chat(usernames)

        if len(usernames) == 1:
            username1 = user.username
            username2 = usernames[0]
        else:
            username1, username2 = usernames[:2]

        room_users_resp = await self.bot.highrise.get_room_users()
        if hasattr(room_users_resp, 'content'):
            users_positions = room_users_resp.content
        else:
            await self.bot.highrise.chat("Failed to get room users.")
            return

        user1 = user2 = pos1 = pos2 = None
        for u, pos in users_positions:
            if u.username.lower() == username1.lower():
                user1, pos1 = u, pos
            elif u.username.lower() == username2.lower():
                user2, pos2 = u, pos
        if not user1 or not user2 or not pos1 or not pos2:
            await self.bot.highrise.chat("Could not find both users in the room.")
            return

        caller_user_id = user.id
        if user1.id == caller_user_id:
            caller_user, caller_pos = user1, pos1
            other_user, other_pos = user2, pos2
        else:
            caller_user, caller_pos = user2, pos2
            other_user, other_pos = user1, pos1

        temp_pos = Position(x=caller_pos.x, y=caller_pos.y, z=caller_pos.z)
        await self.bot.highrise.teleport(caller_user.id, Position(x=other_pos.x, y=other_pos.y, z=other_pos.z - 0.000000000000001))
        await self.bot.highrise.teleport(other_user.id, Position(x=temp_pos.x, y=temp_pos.y, z=temp_pos.z - 0.000000000000001))