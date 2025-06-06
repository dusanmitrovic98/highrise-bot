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
            await self.bot.highrise.chat("Usage: !swap @user1 [@user2 ...]")
            return

        def extract_username(arg):
            return arg.lstrip("@")

        usernames = [extract_username(arg) for arg in args if arg.startswith("@")]
        if not usernames:
            await self.bot.highrise.chat("Please mention at least one user to swap with.")
            return

        # Build the swap order: caller first, then all mentioned users
        swap_usernames = [user.username] + usernames

        room_users_resp = await self.bot.highrise.get_room_users()
        if hasattr(room_users_resp, 'content'):
            users_positions = room_users_resp.content
        else:
            await self.bot.highrise.chat("Failed to get room users.")
            return

        # Map usernames to (user, pos)
        user_map = {}
        for u, pos in users_positions:
            user_map[u.username.lower()] = (u, pos)

        # Collect user objects and positions in swap order
        swap_users = []
        swap_positions = []
        for uname in swap_usernames:
            entry = user_map.get(uname.lower())
            if not entry:
                await self.bot.highrise.chat(f"Could not find user '{uname}' in the room.")
                return
            swap_users.append(entry[0])
            swap_positions.append(entry[1])

        # Store all positions before swapping
        temp_positions = [Position(x=pos.x, y=pos.y, z=pos.z) for pos in swap_positions]

        # Calculate target positions for each user (circular swap)
        n = len(swap_users)
        target_positions = []
        for i in range(n):
            target_index = (i + 1) % n
            target_pos = temp_positions[target_index]
            # Subtract a tiny value from z to avoid collision
            target_positions.append(Position(x=target_pos.x, y=target_pos.y, z=target_pos.z - 0.000000000000001))

        # Teleport all users in parallel
        await asyncio.gather(*[
            self.bot.highrise.teleport(swap_users[i].id, target_positions[i])
            for i in range(n)
        ])